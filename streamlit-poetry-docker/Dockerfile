# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/opt/poetry \
    PATH="/opt/poetry/bin:$PATH"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry into /opt/poetry (not under /root)
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy only dep files first (for caching)
COPY pyproject.toml poetry.lock* ./

# IMPORTANT: install as root because we install into system site-packages
RUN poetry install --no-interaction --no-ansi --no-root

# Now copy app code
COPY . .

# Create non-root user and fix ownership
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Use PORT environment variable for Railway compatibility
ENV PORT=8501
EXPOSE $PORT
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=${PORT}", "--server.maxUploadSize=50", "--browser.gatherUsageStats=false"]
