docker build -t my-python-app .
docker run --name web-container -d -p 5000:5000 my-python-app