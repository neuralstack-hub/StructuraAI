
FROM python:3.12-slim

WORKDIR /app

# Runtime library required by PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy backend application and model files
COPY backend/ ./backend/
COPY ml/ ./ml/

# Create directory for persistent SQLite storage
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
