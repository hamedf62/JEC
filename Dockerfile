# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies into a virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv venv /opt/venv && \
    uv pip install --no-cache -r requirements.txt --python /opt/venv/bin/python

# Prune unnecessary files from the virtual environment
RUN find /opt/venv -type d -name "tests" -exec rm -rf {} + && \
    find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + && \
    find /opt/venv -name "*.pyc" -delete && \
    rm -rf /opt/venv/lib/python*/site-packages/pip \
    /opt/venv/lib/python*/site-packages/setuptools \
    /opt/venv/lib/python*/site-packages/wheel \
    /opt/venv/lib/python*/site-packages/pyarrow # Remove pyarrow to save 120MB+

# --- Stage 2: Final ---
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Copy application code
COPY app/ ./app/
# COPY data/ ./data/

# Expose Streamlit port
EXPOSE 8501

# Health check (using python to avoid installing curl/wget)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Command to run the application
CMD ["streamlit", "run", "app/streamlit_dashboard.py"]
