from flask import Flask, render_template, request
import psycopg
import subprocess
import json
import time
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
    return 'Hello, %s %s! Your random number is: %s. <br/><br/> <a href="/">Back Home</a>' % (first_name, last_name, getRandomNumber("192.1.1.50:3000/randomnumber"))

@app.route('/randomnumber')
def randomnumber():
    return 'Your random number is: %s' % getRandomNumber("192.1.1.50:3000/randomnumber")

@app.route('/trypostgresql')
def trypostgresql():
    with psycopg.connect("postgresql://postgres:password@192.1.1.50:5432") as conn:
        with conn.cursor() as cur:
            #cur.execute("SELECT * FROM test_schema.test_table")

            cur.execute("SELECT row_to_json(t) FROM (SELECT * FROM test_schema.test_table) AS t")
            record = cur.fetchall()
            #for record in cur:
            #   print(record)
    #time.sleep(10)
    return record
    #return 'Your random number is: %s' % getRandomNumber("192.1.1.50:3000/randomnumber")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')