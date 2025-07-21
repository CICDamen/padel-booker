FROM python:3.12-slim

# Install system dependencies for Selenium
RUN apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false && \
    apt-get install -y --allow-unauthenticated --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /tmp/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY src/padel_booker/ ./src/padel_booker/

# Set Python path and Chrome options for headless operation
ENV PYTHONPATH=/app
ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# Expose port for FastAPI service
EXPOSE 8080

# Default command to run the FastAPI service
CMD ["uv", "run", "uvicorn", "src.padel_booker.api:app", "--host", "0.0.0.0", "--port", "8080"]