from flask import Flask, render_template, request
import subprocess
import json
import time
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
    return render_template('test.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    return 'Hello, %s %s! <br/><br/> <a href="/">Back Home</a>' % (first_name, last_name)

@app.route('/trypostgresql')
def trypostgresql():
    return querypostgresql('192.1.1.50:3000/postgresql')
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')