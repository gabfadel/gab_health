# Builder stage
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
 && rm -rf /var/lib/apt/lists/*

# Install pip first to avoid issues
RUN pip install --upgrade pip setuptools wheel

# Copy and install requirements in separate steps
COPY requirements.txt .

# Create wheels for dependencies
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set environment variables properly - these can be overridden from docker-compose
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=False \
    DATABASE_HOST=db \
    DATABASE_PORT=5432

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
 && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]





