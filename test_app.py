import requests
import time

def test_latency():
    start_time = time.time()
    image_path = "./data/test1.jpg"
    with open(image_path, "rb") as file:
        files = {"image": file}
        response = requests.post("http://localhost:8000/predict", files=files)

    end_time = time.time()
    latency = end_time - start_time
    print(f"Latency: {latency} seconds")

if __name__ == "__main__":
    test_latency()
