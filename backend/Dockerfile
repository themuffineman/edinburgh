# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y wget curl libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpangocairo-1.0-0 libgtk-3-0 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium


# Copy the rest of your app
COPY . .

# Expose port (optional if your app serves HTTP)
EXPOSE 3000

# Command to run your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]


