import io
import os
import torch
from PIL import Image
from torchvision import models, transforms
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import psutil
import mlflow
import time
import threading

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

model = models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load the class labels for the ImageNet dataset
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
LABELS_FILE = os.path.basename(LABELS_URL)
LABELS_PATH = os.path.join(os.getcwd(), LABELS_FILE)

if not os.path.exists(LABELS_PATH):
    import urllib.request

    urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)

with open(LABELS_PATH, "r") as f:
    labels = f.read().strip().split("\n")

# Predict the image class
def predict_image_class(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted_idx = torch.max(outputs, 1)
        predicted_label = labels[predicted_idx.item()]

    return predicted_label

# We use a separate thread for the monitoring process to
# constantly monitor the model
def monitor_hardware():
    start_time = time.time()
    while True:
        cpu_percent, memory_percent = psutil.cpu_percent(), psutil.virtual_memory().percent
        latency = time.time() - start_time

        mlflow.log_metric("CPU Usage", cpu_percent)
        mlflow.log_metric("Memory Usage", memory_percent)
        mlflow.log_metric("Latency", latency)

        time.sleep(10)

monitor_thread = threading.Thread(target=monitor_hardware)
monitor_thread.daemon = True
monitor_thread.start()

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    label = predict_image_class(contents)
    return {"label": label}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
