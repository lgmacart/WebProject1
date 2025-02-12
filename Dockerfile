FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install curl

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]