FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r backend/requirements.txt

# Copy source code and assets
COPY backend ./backend
COPY frontend ./frontend
COPY database ./database

# Train machine learning model
RUN python backend/train_classifier.py

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
