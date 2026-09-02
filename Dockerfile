FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for OpenCV, GrabCut, and web scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install all Python libraries required by app.py
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    gunicorn \
    flask \
    flask-login \
    flask-sqlalchemy \
    werkzeug \
    opencv-python-headless \
    numpy \
    pandas \
    cloudscraper \
    beautifulsoup4 \
    lxml \
    pillow \
    scikit-learn \
    tensorflow-cpu

ENV PORT=8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
