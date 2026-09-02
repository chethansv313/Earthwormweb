"""
scratch.py
----------
Diagnostic script to verify:
1. Label mapping in models/crop_identifier_labels.json (all 10 crops).
2. Model loading (crop_identifier_model.keras / .h5).
3. Test prediction accuracy on any sample leaf image.
"""

import json
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# ---------------------------------------------------------------
# 1. VERIFY LABELS
# ---------------------------------------------------------------
LABELS_PATH = os.path.join("models", "crop_identifier_labels.json")

print("=" * 60)
print("1. CHECKING LABEL MAPPINGS")
print("=" * 60)

if os.path.exists(LABELS_PATH):
  with open(LABELS_PATH, "r") as f:
    label_map = json.load(f)
  print("Active Label Mapping:\n", json.dumps(label_map, indent=2))
  print(f"\nTotal Classes Detected: {len(label_map)}")
else:
  print(f"[ERROR] Label file not found at: {LABELS_PATH}")
  label_map = {}

# ---------------------------------------------------------------
# 2. LOAD STAGE-1 IDENTIFIER MODEL
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("2. LOADING IDENTIFIER MODEL")
print("=" * 60)

model = None
for ext in [".keras", ".h5"]:
  model_path = os.path.join("models", f"crop_identifier_model{ext}")
  if os.path.exists(model_path):
    print(f"Found model: {model_path}")
    model = load_model(model_path, compile=False)
    break

if model is None:
  print("[ERROR] No crop_identifier_model (.keras or .h5) found in models/")
  exit()

# ---------------------------------------------------------------
# 3. TEST INFERENCE ON A SAMPLE IMAGE
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("3. RUNNING INFERENCE TEST")
print("=" * 60)

# Replace with any image path on your drive to test
TEST_IMAGE_PATH = r"D:\major project\apple\train\Apple___healthy\image (1).jpg"

# Fallback test search if the default path doesn't exist
if not os.path.exists(TEST_IMAGE_PATH):
  test_dir = r"D:\major project\crop_id\valid"
  if os.path.exists(test_dir):
    for root, _, files in os.walk(test_dir):
      for file in files:
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
          TEST_IMAGE_PATH = os.path.join(root, file)
          break
      if os.path.exists(TEST_IMAGE_PATH):
        break

if os.path.exists(TEST_IMAGE_PATH):
  print(f"Testing image: {TEST_IMAGE_PATH}")

  # Load and preprocess
  img_bgr = cv2.imread(TEST_IMAGE_PATH)
  img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
  img_resized = cv2.resize(img_rgb, (224, 224))
  x = np.expand_dims(img_resized, axis=0).astype("float32") / 255.0

  # Predict
  preds = model.predict(x, verbose=0)[0]

  print("\nProbability Distribution:")
  print("-" * 35)
  for idx, prob in enumerate(preds):
    crop_name = label_map.get(str(idx), f"Class {idx}")
    print(f"  [{idx}] {crop_name:<12} : {prob * 100:>6.2f}%")
  print("-" * 35)

  top_idx = str(np.argmax(preds))
  top_crop = label_map.get(top_idx, "Unknown")
  top_confidence = np.max(preds) * 100

  print(f"\n--> TOP PREDICTION: {top_crop.upper()} ({top_confidence:.2f}%)")
else:
  print(
      f"[WARNING] Test image path not found: {TEST_IMAGE_PATH}\nUpdate"
      " 'TEST_IMAGE_PATH' with a valid image on your D: drive."
  )

print("=" * 60)