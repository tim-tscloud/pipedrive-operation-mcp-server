# Use the official Python image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies directly with pip
RUN pip install --no-cache-dir fastmcp requests

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "server.py"]