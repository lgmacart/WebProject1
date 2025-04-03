docker build -t my-python-app .
docker run --name web-container -v document_volume:/app/documents/store -d -p 5000:5000 my-python-app