# Use official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all bot files to container
COPY . .

# Set environment variables (optional, can use Docker Compose)
ENV API_ID=your_api_id
ENV API_HASH=your_api_hash
ENV BOT_TOKEN=your_bot_token
ENV MONGO_URL=your_mongodb_url
ENV DATABASE_NAME=VideoBot
ENV CHANNEL_ID=-100xxxxxxxxxx
ENV FSUB_CHANNEL=your_channel_username
ENV AUTO_DELETE_TIME=60
ENV OWNER_ID=your_telegram_id

# Run the bot
CMD ["python", "main.py"]
