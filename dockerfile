FROM python:3.12-slim

# Set environment variables to prevent .pyc files and enable output buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port (optional, depending on your Django setup)
EXPOSE 8000

# Run Django app (if using runserver in dev)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
