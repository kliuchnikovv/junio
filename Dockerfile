FROM python:3.11-slim

# Ensure Python output is unbuffered for proper logging in Docker
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT:-3000}

CMD ["python", "app.py"]
