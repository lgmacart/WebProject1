from flask import Flask, render_template, request
import subprocess
import json
import time
import os
import random
from datetime import datetime
import configparser
from classes.db import DB_Connection, DB_Query, DB_Write

app = Flask(__name__)

def connect_to_postgresql(uri):
    connection = DB_Connection(uri, None, None, None)    
    return connection

def query_postgresql(uri, sql):
    connection = connect_to_postgresql(uri)

    if connection.connection is not None:
        query = DB_Query(connection.connection, sql, None, None, None)
        if query.success:
            record = query.result
        else:
            record = query.error.pgresult.error_message   
    else:
        record = connection.error.pgconn.error_message
    return record

def write_to_postgresql(uri, sql):
    connection = connect_to_postgresql(uri)

    if connection.connection is not None:
        query = DB_Write(connection.connection, sql, None, None, None)
        if query.success:
            record = query.result
        else:
            record = query.error.pgresult.error_message   
    else:
        record = connection.error.pgconn.error_message
    return record

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
    return render_template('main.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    return 'Hello, %s %s! <br/><br/> <a href="/">Back Home</a>' % (first_name, last_name)

@app.route('/trypostgresql')
def trypostgresql():
    return querypostgresql('192.1.1.50:3000/postgresql') 

@app.route('/multiupload', methods=['POST'])
def upload_files():
    output_array = []
    is_match = False
    tmp_file_store = "/app/documents/tmp/"
    file_store = "/app/documents/store/"

    config = configparser.ConfigParser()
    config.read(r'./config/db.conf')
    uri = config.get('global', 'uri') 

    files = request.files.getlist('file')
    notes = request.form.getlist('note[]')
    if len(files) > 0:
        note_index = 0
        for file in files:   
            size = len(file.read())
            file.seek(0)
            filename = file.filename

            note = notes[note_index]
            note_index += 1                
            with open("/app/Log.txt", "a") as outfile:
                outfile.write('Note: ' + str(note) + '\n')

            fq_filename_tmp = tmp_file_store + filename
            file.save(fq_filename_tmp) 
            is_file = os.path.isfile(fq_filename_tmp) 
            if is_file: 
                sql = "SELECT unique_id, name FROM dm.file WHERE name = '" + filename + "'"
                query_result = json.loads(query_postgresql(uri, sql))
                if len(query_result) > 0:
                    filename_from_db = query_result[0]['row_to_json']['name']
                    fileid_from_db = query_result[0]['row_to_json']['unique_id']
                else:
                    filename_from_db = filename
                    fileid_from_db = random.randint(1000000,9999999)
                    sql = "INSERT INTO dm.file (unique_id, name, mime_type)" 
                    sql += " VALUES ("
                    sql += str(fileid_from_db) + ", "
                    sql += "'" + filename + "', "
                    sql += "'text'"
                    sql += ")"
                    query_result = write_to_postgresql(uri, sql)

                    with open("/app/Log.txt", "a") as outfile:
                        outfile.write(str(sql) + '\n')
                        outfile.write(str(query_result) + '\n')

                if filename == filename_from_db:
                    sql = "SELECT version, fq_name FROM dm.version WHERE file_id = '" + str(fileid_from_db) + "'"
                    query_result = json.loads(query_postgresql(uri, sql))

                    with open("/app/Log.txt", "a") as outfile:
                        outfile.write(str(query_result) + '\n')                    

                    for row in query_result:                        
                        fq_filename = row['row_to_json']['fq_name']
                        version = row['row_to_json']['version']

                        result = subprocess.run(["diff", "-q", fq_filename_tmp, fq_filename], check=False, capture_output=True).stdout
                        result = len(result)
                        if result == 0:                            
                            is_match = True
                            break
                        else:
                            is_match = False

                    if not is_match:
                        fq_filename = file_store + filename + "." + str(random.randint(10000, 99999))                        
                        result = subprocess.run(["mv", fq_filename_tmp, fq_filename], check=True, capture_output=True).stdout

                        sql = "SELECT max(version) + 1 as nextver FROM dm.version WHERE file_id = '" + str(fileid_from_db) + "'"
                        query_result = json.loads(query_postgresql(uri, sql))
                        
                        with open("/app/Log.txt", "a") as outfile:
                            outfile.write(str(query_result) + '\n') 

                        version = query_result[0]['row_to_json']['nextver']
                        if version is None:
                            version = 1

                        sql = "INSERT INTO dm.version (version, fq_name, description, upload_date, upload_user, size, file_id)" 
                        sql += " VALUES ("
                        sql += str(version) + ", "
                        sql += "'" + fq_filename + "', "
                        sql += "'" + note + "', "
                        sql += "now()" + ", "
                        sql += str(12345) + ", "
                        sql += str(size) + ", "
                        sql += str(fileid_from_db)
                        sql += ")"
                        query_result = write_to_postgresql(uri, sql)

                        with open("/app/Log.txt", "a") as outfile:
                            outfile.write(str(sql) + '\n')
                            outfile.write(str(query_result) + '\n')

                        status = "Uploaded successfully"
                        status_code = 1
                    else:
                        result = subprocess.run(["rm", fq_filename_tmp], check=True, capture_output=True).stdout
                        status = "Files matches version " + str(version)
                        status_code = 0
                else:
                    continue
            else:
                status = "Failed to upload" 

            output = {
                "name" : filename,
                "size" : size,
                "status" : status
            } 

            output_array.append(output)
    else:
        status = "No file selected"
    
    return render_template('main.html', output_list=output_array)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')