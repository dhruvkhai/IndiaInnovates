# Dockerfile for Raspberry Pi waste-classifier service
# Target: Raspberry Pi OS (ARM, 64-bit recommended)
#
# On the Pi, build and run:
#   cd devices/raspi_waste_classifier
#   docker build -t raspi-waste-classifier .
#   docker run --rm -it \
#     --device /dev/video0:/dev/video0 \ 
#     -p 9001:9001 \
#     -e BACKEND_CLASSIFICATION_URL=http://host.docker.internal:8000/raspi/classifications \
#     raspi-waste-classifier
#
# Mounting /dev/video0 gives the container access to the Pi camera (v4l2).

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./main.py

EXPOSE 9001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]

