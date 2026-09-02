FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install all required Python packages
RUN pip install --no-cache-dir \
    gunicorn \
    flask \
    requests \
    cloudscraper \
    beautifulsoup4 \
    lxml \
    opencv-python-headless \
    numpy \
    pandas \
    pillow \
    scipy \
    scikit-learn

# Install extra packages if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

ENV PORT=8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
