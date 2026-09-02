FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install all required Python packages
RUN pip install --no-cache-dir \
    gunicorn \
    flask \
    opencv-python-headless \
    numpy \
    pandas \
    pillow

# Install any extra dependencies if a requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Cloud Run port
ENV PORT=8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
