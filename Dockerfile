FROM python:slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 4000

# CMD ["uvicorn", "main:app", "--reload", "--ssl-keyfile", "./localhost+3-key.pem", "--ssl-certfile", "./localhost+3.pem", "--host", "0.0.0.0", "--port", "4000"]
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-4000}"]

