FROM python:3.12.9-slim

RUN pip install --no-cache-dir \
    Flask==2.3.3 \
    matplotlib==3.10.0\
    pandas==2.2.3
    
WORKDIR /app
COPY . .

CMD ["python", "main.py"]