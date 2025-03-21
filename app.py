from flask import Flask, render_template, request
import subprocess
import json
import time
import os

app = Flask(__name__)

def querypostgresql(uri):
    command = "curl -s " + uri
    #try:
    result = subprocess.run(["curl", "-s", uri], check=True, capture_output=True).stdout
    #except:
    #    return "Junk"
    jsonReturn = json.loads(result)
    return str(jsonReturn["result"])

@app.route('/')
def index():
    return render_template('test2.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    return 'Hello, %s %s! <br/><br/> <a href="/">Back Home</a>' % (first_name, last_name)

@app.route('/trypostgresql')
def trypostgresql():
    return querypostgresql('192.1.1.50:3000/postgresql')

@app.route('/upload', methods=['POST'])
def upload_file():
    file_store = "/app/documents/"
    if 'file' not in request.files:
        message = "Invalid selection"
    else:
        file = request.files['file']
        if file.filename == '':
            message = "No file selected"            
        else:
            # Save the file or process it as needed
            filename = file.filename
            fq_filename = file_store + filename
            is_file = os.path.isfile(fq_filename)
            if is_file:
                message = "File already exists"
            else:
                file.save(fq_filename)
                is_file = os.path.isfile(fq_filename) 
                if is_file:        
                    message = "Uploaded successfully"
                else:
                    message = "Failed to load"

    return render_template('test2.html', message=message, filename=filename)   
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')