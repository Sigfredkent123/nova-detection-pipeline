# Use the exact Python version you want
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy local files
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Streamlit port
EXPOSE 8080

# Streamlit entrypoint
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
