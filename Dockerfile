FROM python:3.9

WORKDIR /app

COPY app.py .
COPY test_app.py .
COPY requirements.txt .
COPY static static

RUN pip install -r requirements.txt

# Expose the port that the FastAPI app will listen on
EXPOSE 8000

# Run the FastAPI app when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
