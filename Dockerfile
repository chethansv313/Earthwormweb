FROM python:3.10-slim

WORKDIR /app

# Install dependencies if requirements.txt exists
COPY requirements.txt ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy all application files
COPY . .

# Run the Flask app on the Cloud Run PORT
ENV PORT=8080
CMD ["python", "app.py"]
