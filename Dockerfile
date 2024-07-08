# Use the official Python image as the base image
FROM python:3.12.3-slim

# Set environment variables
# To stop Python from creating .pywc files for all the files
ENV PYTHONDONTWRITEBYTECODE 1
# Stops unbuffering
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /pcfeApp
# COPY Pipfile Pipfile.lock /pcfeApp/
# Installing the .env file at the system level
# RUN pip install pipenv && pipenv install --system
# Docker itself is like a VM - so need to create a virtual environment
# Install dependencies
COPY requirements.txt /pcfeApp/
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project code into the container
COPY . /pcfeApp/

# Collect static files
RUN python manage.py collectstatic --no-input

# Change ownership of static files
RUN addgroup --system proxy && adduser --system --no-create-home --group proxy

# Set static files permissions
RUN chown -R proxy:proxy /pcfeApp/static/

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Set the command to start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "CorePCFE.wsgi:application"]
