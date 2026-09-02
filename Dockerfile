FROM python:3.10-slim

WORKDIR /app

# Copy application files
COPY . .

# Install dependencies and production web server
RUN pip install --no-cache-dir gunicorn
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir flask; fi

# Default Cloud Run port
ENV PORT=8080

# Run with Gunicorn on 0.0.0.0:$PORT
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
