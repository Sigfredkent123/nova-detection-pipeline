# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p output/eye

# Expose Flask port
EXPOSE 10000

# Start Flask app
CMD ["python", "app.py"]
