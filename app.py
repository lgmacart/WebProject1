from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    return 'Hello, %s %s! Have fun learning python. <br/> <a href="/">Back Home</a>' % (first_name, last_name)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')