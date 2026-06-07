# =====================================================================
# STAGE 1: Builder
# =====================================================================
FROM python:3.11-slim-bookworm AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements list
COPY requirements.txt .

# Install uv package manager inside builder stage
# We use BuildKit cache mounts for uv downloads to speed up subsequent rebuilds.
RUN pip install --no-cache-dir uv

# Install headless OpenCV, CPU-only PyTorch, and requirements using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system opencv-python-headless && \
    uv pip install --system torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install --system -r requirements.txt

# =====================================================================
# STAGE 2: Runtime
# =====================================================================
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

# Install runtime dependencies:
# - r-base: required for executing R statistics scripts
# - curl: required for container healthcheck
# (Note: libgl1-mesa-glx and libglib2.0-0 are no longer needed because we use opencv-python-headless!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a secure non-root user and group
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser && \
    chown -R appuser:appgroup /app

# Copy the rest of the application files with non-root ownership
COPY --chown=appuser:appgroup . .

# Run container as non-root user for security hardening
USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck to verify Streamlit server status
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Launch the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
