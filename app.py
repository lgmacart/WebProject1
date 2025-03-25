from flask import Flask, render_template, request
import subprocess
import json
import time
import os
import random
from datetime import datetime

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
    status = ""        
    is_match = False
    tmp_file_store = "/app/documents/tmp/"
    file_store = "/app/documents/store/"
    if 'file' not in request.files:
        status = "Invalid selection"
    else:
        file = request.files['file']     
        size = len(file.read())
        file.seek(0)
        if file.filename == '':
            status = "No file selected"            
        else:
            filename = file.filename
            fq_filename_tmp = tmp_file_store + filename
            fq_filename = file_store + filename + "." + str(random.randint(10000, 99999))
            is_file = os.path.isfile(fq_filename_tmp)
            if is_file:                
                status = "File already exists in tmp"
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
                        status = "Uploaded successfully"
                    else:
                        result = subprocess.run(["rm", fq_filename_tmp], check=True, capture_output=True).stdout
                        status = "Files matches an existing file"
                    
                else:
                    status = "Failed to load"

    return render_template('test2.html', status=status, filename=filename, size=size) 

@app.route('/multiupload', methods=['POST'])
def upload_files():
    file_attribute_array = []
    owner = "len"
    upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = ""
    status_code = 0
    is_match = False
    tmp_file_store = "/app/documents/tmp/"
    file_store = "/app/documents/store/"
    if 'file' not in request.files:
        status = "Invalid selection"
    else:
        files = request.files.getlist('file') 
        for file in files:   
            size = len(file.read())
            file.seek(0)
            if file.filename == '':
                status = "No file selected"            
            else:
                filename = file.filename
                fq_filename_tmp = tmp_file_store + filename
                fq_filename = file_store + filename + "." + str(random.randint(10000, 99999))
                is_file = os.path.isfile(fq_filename_tmp)
                if is_file:                
                    status = "File already exists in tmp"
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
                            status = "Uploaded successfully"
                            status_code = 1
                        else:
                            result = subprocess.run(["rm", fq_filename_tmp], check=True, capture_output=True).stdout
                            status = "Files matches an existing file"
                            status_code = 0
                        
                    else:
                        status = "Failed to load"
            file_attribute = {
                'name' : filename,
                'size' : size,
                'status' : status,
                'status_code' : status_code,
                'owner' : owner,
                'date' : upload_date,
                'fq_name' : fq_filename
            }

            file_attribute_array.append(file_attribute)

    with open("/app/fauxDB.json", "a") as outfile:
        for file_attribute in file_attribute_array:
            if file_attribute['status_code'] == 1:
                json.dump(file_attribute, outfile)
                outfile.write('\n')
    
    return render_template('test2.html', files=file_attribute_array)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')