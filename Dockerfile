# Use Playwright's Python image which already includes browser binaries and system deps
FROM mcr.microsoft.com/playwright/python:latest

# Prevent Python buffering so logs show up immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip deps (uses your repo's requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Ensure Playwright browsers are installed (image usually already has them; this is idempotent)
RUN playwright install --with-deps || true

EXPOSE 8000

# Run the backend (Flask dev server as in your repo)
CMD ["python", "backend/main.py"]
