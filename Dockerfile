# Base Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install dependencies
RUN poetry install --no-root --only main

# Copy the entire project (your code)
COPY . .

# Expose Django port
EXPOSE 8000

# Default command (runs the server)
CMD poetry run python api/manage.py collectstatic --no-input && \
    poetry run python api/manage.py migrate && \
    poetry run python api/superuser_setup.py && \
    poetry run python api/manage.py runserver 0.0.0.0:8000
