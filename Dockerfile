# Use lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir \
    python-telegram-bot==13.15 \
    requests \
    beautifulsoup4 \
    flask

# Expose port for dummy health check server
EXPOSE 8000

# Run the bot
CMD ["python", "app.py"]
