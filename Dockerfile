FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements_gui.txt ./requirements.txt

# Install CPU-only PyTorch
RUN pip install --no-cache-dir \
    torch \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies without replacing CPU-only PyTorch
RUN sed -i '/^sentence-transformers$/d' requirements.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps sentence-transformers

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
