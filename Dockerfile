# Base image with stable Python 3.13
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Default command (adjust as needed)
CMD ["python", "./app/main.py"]
