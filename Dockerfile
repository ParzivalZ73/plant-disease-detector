FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/
COPY model/plant_model.keras ./model/plant_model.keras
COPY model/classes.json ./model/classes.json

WORKDIR /app/app

ENV MODEL_PATH=/app/model/plant_model.keras
ENV CLASSES_PATH=/app/model/classes.json

EXPOSE 5000

CMD ["python", "app.py"]
