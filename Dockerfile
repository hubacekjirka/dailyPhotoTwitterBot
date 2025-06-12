# Base image with Python 3.13 (use official or custom-built until officially available)
FROM python:3.13-rc-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install pip-tools for compiling requirements
RUN pip install --upgrade pip pip-tools

# Copy your requirements file
COPY requirements.in .

# Compile requirements.txt
RUN pip-compile requirements.in

# Install compiled dependencies
RUN pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Default command (adjust as needed)
CMD ["python", "./app/main.py"]
