# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
#ENV GOOGLE_CLOUD_PROJECT=citric-hawk-424815-k9
#ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]