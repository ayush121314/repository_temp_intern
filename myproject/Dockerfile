# Use the official Python image as the base image
FROM python:3.9-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt /app/

# Install system dependencies for PDF generation and other required libraries
RUN apt-get update && apt-get install -y \
    libglib2.0-dev \
    libgtk-3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libpango1.0-0\
    libgdk-pixbuf2.0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000 to access the Django app
EXPOSE 8000

# Set Django settings module
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# Run Django's development server on container start
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
