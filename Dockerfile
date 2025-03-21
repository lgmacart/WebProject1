FROM python:3.9-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install curl

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /app/documents

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]