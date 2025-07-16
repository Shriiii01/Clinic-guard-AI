FROM python:3.11

# 🔧 Install required build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    git \
    curl

WORKDIR /app
COPY ./server /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
