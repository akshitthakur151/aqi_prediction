FROM python:3.10-slim

LABEL maintainer="AQI Prediction Team"
LABEL description="Air Quality Index Prediction System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/advanced.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r advanced.txt

# Copy project files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 8501 5000

# Default command
CMD ["python", "main.py", "--api", "fastapi"]
