FROM python:3.10-slim

WORKDIR /app

# Copy all project files into the container
COPY . .

# Install dependencies if requirements.txt exists, otherwise install basic web dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir flask; fi

# Default Cloud Run environment port
ENV PORT=8080

CMD ["python", "app.py"]
