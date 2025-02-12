from flask import Flask, render_template, request
import subprocess
import json

app = Flask(__name__)

def getRandomNumber(uri):
    command = "curl -s " + uri
    #try:
    result = subprocess.run(["curl", "-s", uri], check=True, capture_output=True).stdout
    #except:
    #    return "Junk"
    jsonReturn = json.loads(result)
    return str(jsonReturn["number"])

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    return 'Hello, %s %s! Have fun learning Python. <br/> <a href="/">Back Home</a>' % (first_name, last_name)

@app.route('/randomnumber')
def randomnumber():
    return 'Your random number is: %s' % getRandomNumber("192.1.1.50:3000/randomnumber")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')