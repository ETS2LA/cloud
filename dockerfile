# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the current directory into the container
COPY . .

# Expose the port that the server will listen on
EXPOSE 8000

# Set the command to run when the container starts
CMD ["python", "main.py"]

# Add a healthcheck
HEALTHCHECK --interval=5m --timeout=3s \
    CMD curl -f http://localhost:8000/heartbeat || exit 1