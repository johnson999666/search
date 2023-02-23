
from flask import Flask, render_template




app = Flask(__name__)



def hello():
    return "Hello World!"


@app.route('/')
def home():
    re = hello()
    return render_template("index.html", re=re)


if __name__ == "__main__":
    app.run(debug=True)
