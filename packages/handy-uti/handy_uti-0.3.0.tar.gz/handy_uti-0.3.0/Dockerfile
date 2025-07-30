FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    build-essential \
    libxml2-dev \
    libxslt1-dev && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies with uv
RUN uv sync --frozen || uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 8211

# Run the application
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8211", "--server.address=0.0.0.0"]
