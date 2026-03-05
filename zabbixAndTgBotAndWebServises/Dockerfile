FROM python:3.11-slim
RUN pip install flask paho-mqtt
WORKDIR /app
COPY . .
CMD ["python", "app.py"]
