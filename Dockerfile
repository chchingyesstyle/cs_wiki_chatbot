FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including build tools for llama-cpp-python)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for ChromaDB and models
RUN mkdir -p /app/chroma_db /app/models

# Expose ports
EXPOSE 5000 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check (increased timeout for slow LLM responses)
HEALTHCHECK --interval=30s --timeout=60s --start-period=120s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=50)" || exit 1

# Default command - can be overridden
CMD ["python", "app.py"]
