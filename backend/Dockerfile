FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-railway.txt .
RUN pip install --no-cache-dir -r requirements-railway.txt

COPY . .

# Install heavy AI deps at container start (cached in image)
RUN pip install --no-cache-dir opencv-python-headless mediapipe scipy scikit-image matplotlib seaborn onnxruntime 2>&1 | tail -3 || echo "Some AI deps may fail, will load lazily"

ENV PORT=8000
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
