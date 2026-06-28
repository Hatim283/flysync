# Dockerfile for FastAPI Backend
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port (Cloud Run defaults to 8080)
EXPOSE 8080

# Command to run the application, listening on the Cloud Run PORT environment variable
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
