FROM python:3.12.6-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY client.py /app/client.py

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "client.py"]