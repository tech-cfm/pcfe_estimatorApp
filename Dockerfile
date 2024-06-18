# Use the official Python image as the base image
FROM python:3.12.3-slim

# Set environment variables
# To stop Python from creating .pywc files for all the files
ENV PYTHONDONTWRITEBYTECODE 1
# Stops unbuffering
ENV PYTHONUNBUFFERED 1
# Create a non-root user
RUN addgroup --system django && adduser --system --group django

# Set work directory/create a new work directory called app
# Create and set the working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /usr/src/app/
# Copy the entrypoint.sh script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Change to the non-root user
USER django
# Expose the port uWSGI will run on
EXPOSE ${PORT}
# Define environment variable
# ENV NAME World

# Run entrypoint script
ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]