# Use official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Flask health check
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]
