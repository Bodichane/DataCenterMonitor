FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DOCKER_ENV=1
EXPOSE 8080
CMD ["python", "app.py"]
