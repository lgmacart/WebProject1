from flask import Flask, render_template, request
import subprocess
import json
import time
import os
import random

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
    message = ""
    is_match = False
    tmp_file_store = "/app/documents/tmp/"
    file_store = "/app/documents/store/"
    if 'file' not in request.files:
        message = "Invalid selection"
    else:
        file = request.files['file']        
        size = len(file.read())
        file.seek(0)
        if file.filename == '':
            message = "No file selected"            
        else:
            # Save the file or process it as needed            
            filename = file.filename
            fq_filename_tmp = tmp_file_store + filename
            #fq_filename = file_store + filename
            fq_filename = file_store + filename + "." + str(random.randint(10000, 99999))
            is_file = os.path.isfile(fq_filename_tmp)
            if is_file:                
                message = "File already exists in tmp"
            else:
                file.save(fq_filename_tmp) 
                is_file = os.path.isfile(fq_filename_tmp) 
                if is_file:
                    arr = os.listdir(file_store)
                    for file in arr:
                        if file.startswith(filename):
                            file = file_store + file
                            result = subprocess.run(["diff", "-q", fq_filename_tmp, file], check=False, capture_output=True).stdout
                            result = len(result)
                            if result == 0:                            
                                is_match = True
                                break
                            else:
                                is_match = False

                    if not is_match:
                        result = subprocess.run(["mv", fq_filename_tmp, fq_filename], check=True, capture_output=True).stdout                  
                        message = "Uploaded successfully"
                    else:
                        result = subprocess.run(["rm", fq_filename_tmp], check=True, capture_output=True).stdout
                        message = "Files matches an existing file"
                    
                else:
                    message = "Failed to load"

    return render_template('test2.html', message=message, filename=filename, size=size)   
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')