FROM python:3.9-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install curl

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /app/documents
RUN mkdir /app/documents/tmp
RUN mkdir /app/documents/store

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]