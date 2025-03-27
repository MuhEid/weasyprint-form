# Use official Python slim image
FROM python:3.11-slim

# Install system dependencies needed by WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libglib2.0-0 \
    fontconfig \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn (used to run the app in production)
RUN pip install gunicorn

# Copy the entire app
COPY . .

# Expose the Flask port
EXPOSE 5000

# Run the app using Gunicorn (production-grade)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
