# Use the official Python base image
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libmagic1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app


# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
# RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

WORKDIR /app/app

# RUN mkdir /data

# Create the gdpr user and group
# RUN groupadd -r gdpr && useradd -r -g gdpr -m gdpr \
#     && chown -R gdpr:gdpr /app /data

# USER gdpr

# Expose the port on which the application will run
# EXPOSE 8000

# Run the FastAPI application using uvicorn server
# CMD ["uvicorn", "app.main:get_app()", "--host", "0.0.0.0", "--port", "8000", "--reload"]
