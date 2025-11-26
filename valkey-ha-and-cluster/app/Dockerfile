FROM python:3.12-slim

# Docker CLI 설치
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt setuptools

COPY . .

CMD ["python", "ha_test.py"]
