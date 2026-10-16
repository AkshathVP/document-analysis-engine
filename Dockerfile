# Use official lightweight Python runtime as a parent image
FROM python:3.10-slim

# # Configure Python output and local Hugging Face model caching
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for PyMuPDF (fitz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmudraw0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download and cache the Sentence-Transformer model during image build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Prevent model downloads during container runtime
ENV TRANSFORMERS_OFFLINE=1

# Copy the core pipeline scripts into the container
COPY pipeline.py .

# Create directory for input and output documents
RUN mkdir -p /app/input_docs

# Default execution command
CMD ["python", "pipeline.py", "--input", "/app/input_docs/sample.pdf", "--output", "/app/outline.json"]
