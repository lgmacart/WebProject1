FROM python:3.9-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install curl
RUN apt-get -y install python3-dev libpq-dev gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]