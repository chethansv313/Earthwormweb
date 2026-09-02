"""
app.py
------
Production-Ready Unified Flask Application for Earthworm.
Features:
- Relative cloud-compatible pathing (AWS Elastic Beanstalk / Linux ready)
- User Authentication with persistent SQLite/PostgreSQL storage
- 2-Stage Plant Pathology Pipeline (Leaf Validation -> Crop Router -> Disease Diagnosis)
- Educational Agronomic Knowledge Base Integration (Biological Causes & Action Plans)
- District-Level Live Mandi Price Scraping with Automatic Historical CSV Fallback
- Autoregressive Multi-Step LSTM Market Price Forecasting (Dual ₹/Quintal & ₹/kg)
"""

import base64
import json
import os
import pickle
import re
import cv2
import numpy as np
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from disease_knowledge import get_disease_details
from utils import extract_leaf_with_grabcut, is_valid_leaf

# Safe TensorFlow CPU / GPU loading
try:
  import tensorflow as tf
  from tensorflow.keras.models import load_model

  TF_AVAILABLE = True
except ImportError:
  TF_AVAILABLE = False

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "earthworm-production-secret-key-2026"
)

# ---------------------------------------------------------------
# PATH & ENVIRONMENT CONFIGURATION (CLOUD RELATIVE)
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------------
db_url = os.environ.get("DATABASE_URL", "sqlite:///users.db")
if db_url.startswith("postgres://"):
  db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------------------------------------------------------
# 10-CROP CONFIGURATION MAPPING
# ---------------------------------------------------------------
CROP_CONFIG = {
    "apple": {
        "market_url": "https://www.commodityonline.com/mandiprices/apple/jammu-and-kashmir",
        "csv_file": os.path.join(DATA_DIR, "apple datasets.csv"),
        "default_price": 6000.00,
        "lookback": 30,
    },
    "corn": {
        "market_url": "https://www.commodityonline.com/mandiprices/maize/karnataka/davangere",
        "csv_file": os.path.join(DATA_DIR, "corn datasets.csv"),
        "default_price": 2100.00,
        "lookback": 30,
    },
    "cotton": {
        "market_url": "https://www.commodityonline.com/mandiprices/cotton/gujarat",
        "csv_file": os.path.join(DATA_DIR, "cotton datasets.csv"),
        "default_price": 7200.00,
        "lookback": 30,
    },
    "grape": {
        "market_url": "https://www.commodityonline.com/mandiprices/grapes/maharashtra/pune",
        "csv_file": os.path.join(DATA_DIR, "grape datasets.csv"),
        "default_price": 5500.00,
        "lookback": 30,
    },
    "onion": {
        "market_url": "https://www.commodityonline.com/mandiprices/onion/maharashtra",
        "csv_file": os.path.join(DATA_DIR, "onion_daily_prices_cleaned.csv"),
        "default_price": 1800.00,
        "lookback": 30,
    },
    "potato": {
        "market_url": "https://www.commodityonline.com/mandiprices/potato/uttar-pradesh/agra",
        "csv_file": os.path.join(DATA_DIR, "POTATO.csv"),
        "default_price": 1350.00,
        "lookback": 30,
    },
    "rice": {
        "market_url": "https://www.commodityonline.com/mandiprices/district/uttar-pradesh/lakhimpur/rice",
        "csv_file": os.path.join(DATA_DIR, "RICEPRED.csv"),
        "default_price": 2950.00,
        "lookback": 30,
    },
    "sugarcane": {
        "market_url": "https://www.commodityonline.com/mandiprices/sugarcane/madhya-pradesh",
        "csv_file": os.path.join(DATA_DIR, "sugarcane datasets.csv"),
        "default_price": 340.00,
        "lookback": 20,
    },
    "tomato": {
        "market_url": "https://www.commodityonline.com/mandiprices/district/madhya-pradesh/dewas/tomato",
        "csv_file": os.path.join(DATA_DIR, "TOMATONEW1.csv"),
        "default_price": 2100.00,
        "lookback": 30,
    },
    "wheat": {
        "market_url": "https://www.commodityonline.com/mandiprices/wheat/uttar-pradesh/hardoi",
        "csv_file": os.path.join(DATA_DIR, "wheat datasets.csv"),
        "default_price": 2350.00,
        "lookback": 30,
    },
}

VALID_CROPS = tuple(CROP_CONFIG.keys())


def load_model_safely(base_filename):
  """Loads Keras models safely (.keras or .h5) from the models directory."""
  for ext in [".keras", ".h5"]:
    path = os.path.join(MODELS_DIR, f"{base_filename}{ext}")
    if os.path.exists(path):
      return load_model(path, compile=False)
  return None


# ---------------------------------------------------------------
# PRICE INGESTION & DATA PREPARATION ENGINE
# ---------------------------------------------------------------
def fetch_csv_fallback_price(crop_name):
  """Extracts the latest modal price from the local historical CSV dataset."""
  cfg = CROP_CONFIG.get(crop_name, {})
  file_path = cfg.get("csv_file")
  fallback_price = cfg.get("default_price", 2000.00)

  try:
    if file_path and os.path.exists(file_path):
      df = pd.read_csv(file_path, sep=None, engine="python")
      col = (
          "Avg_Modal_Price"
          if "Avg_Modal_Price" in df.columns
          else (
              "Modal_Price"
              if "Modal_Price" in df.columns
              else "Modal Price (Rs./Quintal)"
          )
      )
      valid_prices = df[col].dropna()
      if not valid_prices.empty:
        return float(valid_prices.iloc[-1]), "csv_history"
  except Exception:
    pass
  return fallback_price, "default_estimate"


def fetch_live_price(crop_name):
  """Scrapes live market prices with automatic CSV fallback if blocked or closed."""
  try:
    cfg = CROP_CONFIG.get(crop_name, {})
    url = cfg.get("market_url")
    if not url:
      return fetch_csv_fallback_price(crop_name)

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )
    response = scraper.get(url, timeout=10)
    if response.status_code != 200:
      return fetch_csv_fallback_price(crop_name)

    soup = BeautifulSoup(response.text, "html.parser")
    summary_elements = soup.find_all(
        ["div", "span", "td", "li"],
        string=re.compile(r"Quintal|₹|Rs", re.IGNORECASE),
    )
    for elem in summary_elements:
      text = elem.text.replace(",", "").strip()
      match = re.search(
          r"(?:₹|Rs\.?)\s*(\d{3,}(?:\.\d+)?)", text, re.IGNORECASE
      )
      if match:
        price = float(match.group(1))
        if 200 < price < 35000:
          return price, "live"

    return fetch_csv_fallback_price(crop_name)
  except Exception:
    return fetch_csv_fallback_price(crop_name)


# ---------------------------------------------------------------
# USER AUTHENTICATION & PERSISTENCE
# ---------------------------------------------------------------
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)


@login_manager.user_loader
def load_user(user_id):
  return db.session.get(User, int(user_id))


@app.route("/", methods=["GET"])
def root():
  return (
      redirect(url_for("dashboard"))
      if current_user.is_authenticated
      else redirect(url_for("login"))
  )


@app.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("dashboard"))
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
      login_user(user, remember=True)
      return redirect(url_for("dashboard"))
    flash("Invalid User ID or Password. Please try again.")
  return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for("dashboard"))
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if User.query.filter_by(username=username).first():
      flash("User ID already exists. Please choose another.")
      return redirect(url_for("register"))
    db.session.add(
        User(username=username, password_hash=generate_password_hash(password))
    )
    db.session.commit()
    flash("Account created successfully! Please log in.")
    return redirect(url_for("login"))
  return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
  return render_template("dashboard.html", username=current_user.username)


# ---------------------------------------------------------------
# 2-STAGE CROP HEALTH DIAGNOSTICS
# ---------------------------------------------------------------
@app.route("/health")
@login_required
def health_menu():
  return render_template("health_menu.html", crops=VALID_CROPS)


@app.route("/health/<crop_name>", methods=["GET", "POST"])
@login_required
def health_crop(crop_name):
  if crop_name not in VALID_CROPS:
    return "Invalid crop", 404

  result = None
  if request.method == "POST":
    file = request.files.get("leaf_image")
    camera_data = request.form.get("leaf_image_capture")
    filepath = None

    try:
      # Ingest Upload or Live Camera Stream
      if file and file.filename != "":
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
      elif camera_data and "," in camera_data:
        _, encoded = camera_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        filename = f"capture_{crop_name}_temp.jpg"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        with open(filepath, "wb") as f:
          f.write(image_bytes)

      if filepath and TF_AVAILABLE:
        with open(filepath, "rb") as f:
          raw_image_bytes = f.read()

        # Gatekeeper: GrabCut Segmentation & Chlorophyll Analysis
        segmented_img_bgr, foreground_mask = extract_leaf_with_grabcut(
            raw_image_bytes
        )
        if segmented_img_bgr is None:
          raise ValueError("Image segmentation failed.")

        is_leaf, leaf_check_reason = is_valid_leaf(
            segmented_img_bgr, foreground_mask
        )
        if not is_leaf:
          result = {"status": "rejected", "reason": leaf_check_reason}
        else:
          segmented_img_rgb = cv2.cvtColor(segmented_img_bgr, cv2.COLOR_BGR2RGB)
          segmented_resized = cv2.resize(segmented_img_rgb, (224, 224))
          x = (
              np.expand_dims(segmented_resized, axis=0).astype("float32")
              / 255.0
          )

          # STAGE 1: 10-Crop Router Verification
          id_model = load_model_safely("crop_identifier_model")
          labels_path = os.path.join(MODELS_DIR, "crop_identifier_labels.json")

          if id_model and os.path.exists(labels_path):
            with open(labels_path, "r") as f:
              label_map = json.load(f)

            id_preds = id_model.predict(x, verbose=0)
            id_confidence = float(np.max(id_preds[0]))
            id_class_idx = str(np.argmax(id_preds[0]))
            predicted_crop = label_map.get(id_class_idx, "").lower().strip()

            clean_predicted = predicted_crop.rstrip("s")
            clean_target = crop_name.lower().strip().rstrip("s")

            if id_confidence < 0.50 or clean_predicted != clean_target:
              result = {
                  "status": "wrong_crop",
                  "reason": (
                      f"Detected '{predicted_crop.capitalize()}'"
                      f" ({id_confidence:.1%}). Please upload a"
                      f" {crop_name.capitalize()} leaf."
                  ),
              }
            else:
              # STAGE 2: Individual Crop Disease Diagnosis
              disease_model = load_model_safely(f"health_{crop_name}_model")
              health_labels_path = os.path.join(
                  MODELS_DIR, f"health_{crop_name}_labels.json"
              )

              if disease_model:
                d_preds = disease_model.predict(x, verbose=0)
                d_confidence = float(np.max(d_preds[0]))
                d_class_idx = str(np.argmax(d_preds[0]))

                raw_disease_label = f"{crop_name} Healthy"
                if os.path.exists(health_labels_path):
                  with open(health_labels_path, "r") as lf:
                    disease_label_map = json.load(lf)
                    raw_disease_label = disease_label_map.get(
                        d_class_idx, raw_disease_label
                    )

                # Agronomic cause and treatment lookup
                title, cause, treatment = get_disease_details(
                    crop_name, raw_disease_label
                )

                result = {
                    "status": "ok",
                    "prediction": title,
                    "confidence": d_confidence,
                    "cause": cause,
                    "treatment": treatment,
                }
              else:
                result = {
                    "status": "error",
                    "reason": (
                        f"Health model for {crop_name.capitalize()} missing in"
                        " models/."
                    ),
                }
          else:
            result = {
                "status": "error",
                "reason": "Stage-1 Crop Identifier model or labels missing.",
            }
      else:
        result = {
            "status": "error",
            "reason": "No valid image uploaded or TensorFlow unavailable.",
        }
    except Exception as e:
      result = {"status": "error", "reason": str(e)}

  return render_template("health_crop.html", crop_name=crop_name, result=result)


# ---------------------------------------------------------------
# AUTOREGRESSIVE LSTM PRICE FORECASTING
# ---------------------------------------------------------------
@app.route("/price")
@login_required
def price_menu():
  return render_template("price_menu.html", crops=VALID_CROPS)


@app.route("/price/<crop_name>", methods=["GET", "POST"])
@login_required
def price_crop(crop_name):
  if crop_name not in VALID_CROPS:
    return "Invalid crop", 404

  cfg = CROP_CONFIG[crop_name]
  lookback = cfg.get("lookback", 30)
  default_price = cfg["default_price"]
  today_price = default_price
  price_source = "default_estimate"
  recent_prices = []

  try:
    # 1. Load lookback window from historical records
    file_path = cfg.get("csv_file")
    if file_path and os.path.exists(file_path):
      df = pd.read_csv(file_path, sep=None, engine="python")
      col = (
          "Avg_Modal_Price"
          if "Avg_Modal_Price" in df.columns
          else (
              "Modal_Price"
              if "Modal_Price" in df.columns
              else "Modal Price (Rs./Quintal)"
          )
      )
      valid_prices = df[col].dropna()
      if len(valid_prices) >= lookback:
        recent_prices = valid_prices.tail(lookback).tolist()

    if len(recent_prices) < lookback:
      recent_prices = [default_price] * lookback

    # 2. Ingest live price and update the current time-step
    live_price, price_source = fetch_live_price(crop_name)
    if live_price is not None:
      today_price = live_price
      recent_prices[-1] = today_price

    # 3. Load LSTM neural network and scaler artifacts
    lstm_model = load_model_safely(f"price_{crop_name}_model")
    scaler_pkl_path = os.path.join(
        MODELS_DIR, f"price_{crop_name}_scaler.pkl"
    )

    if (
        TF_AVAILABLE
        and lstm_model
        and os.path.exists(scaler_pkl_path)
        and len(recent_prices) >= lookback
    ):
      with open(scaler_pkl_path, "rb") as f:
        scaler = pickle.load(f)

      scaled_input = scaler.transform(
          np.array(recent_prices[-lookback:]).reshape(-1, 1)
      )
      current_seq = scaled_input.reshape(1, lookback, 1)
      future_scaled_preds = []

      # 4. Multi-step autoregressive rolling forecast (7 Days)
      for _ in range(7):
        pred_scaled = lstm_model.predict(current_seq, verbose=0)[0, 0]
        future_scaled_preds.append(pred_scaled)
        current_seq = np.append(current_seq[:, 1:, :], [[[pred_scaled]]], axis=1)

      forecast = (
          scaler.inverse_transform(
              np.array(future_scaled_preds).reshape(-1, 1)
          )
          .flatten()
          .round(2)
          .tolist()
      )
    else:
      forecast = [round(today_price, 2)] * 7

  except Exception:
    forecast = [round(today_price, 2)] * 7
    price_source = "default_estimate"

  price_source_labels = {
      "live": "Live Mandi Web Scraper",
      "csv_history": "Historical Mandi Records",
      "default_estimate": "Benchmark Market Estimate",
  }

  return render_template(
      "price_crop.html",
      crop_name=crop_name,
      today_price_quintal=round(today_price, 2),
      forecast_quintal=[round(p, 2) for p in forecast],
      today_price_kg=round(today_price / 100, 2),
      forecast_kg=[round(p / 100, 2) for p in forecast],
      prediction_triggered=True,
      price_source=price_source,
      price_source_label=price_source_labels.get(
          price_source, "Benchmark Estimate"
      ),
  )


# ---------------------------------------------------------------
# SERVER ENTRY POINT
# ---------------------------------------------------------------


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
