FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable immediate log streaming
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install Linux system libraries required for OpenCV & image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy application source code
COPY . .

# 3. Install all essential Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    # Web framework & production server
    flask \
    gunicorn \
    werkzeug \
    requests \
    # Computer Vision & Image Processing
    opencv-python-headless \
    pillow \
    scikit-image \
    # Data Science, Math & ML
    numpy \
    pandas \
    scipy \
    scikit-learn \
    joblib \
    matplotlib \
    seaborn \
    # Data storage & file handling
    openpyxl \
    h5py

# 4. Install extra dependencies from requirements.txt if present
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Cloud Run default port
ENV PORT=8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
