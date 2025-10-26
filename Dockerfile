# Use Playwright's Python image which typically includes browser binaries and system deps.
# Pin the image in CI for stable builds (e.g. mcr.microsoft.com/playwright/python:1.37.0-focal)
FROM mcr.microsoft.com/playwright/python:latest

# Prevent Python buffering so logs show up immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip deps first and leverage Docker layer cache by copying only requirements.txt.
# This avoids re-running pip install when app source files change.
COPY requirements.txt ./
# Use a pip cache mount (BuildKit) for faster repeated installs if supported during build.
# Example (requires DOCKER_BUILDKIT=1):
# RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source after installing deps so code changes don't bust the pip layer
COPY . .

# The Playwright base image usually already includes browser binaries. If you need to
# force-install browsers (rare for iterative local builds), pass --build-arg FORCE_PLAYWRIGHT_INSTALL=1
ARG FORCE_PLAYWRIGHT_INSTALL=0
RUN if [ "$FORCE_PLAYWRIGHT_INSTALL" = "1" ] ; then \
    playwright install --with-deps ; \
    else \
    echo "Skipping playwright install (base image likely includes browsers). Set FORCE_PLAYWRIGHT_INSTALL=1 to force." ; \
    fi

# Advanced: to cache Playwright downloads between builds with BuildKit use:
# RUN --mount=type=cache,target=/ms-playwright-cache playwright install --with-deps
# (You must enable BuildKit: $env:DOCKER_BUILDKIT = '1'; docker build ...)

EXPOSE 8000

# Run the backend (Flask dev server as in your repo)
CMD ["python", "backend/main.py"]
