from flask import Flask, render_template
import src.utils as utils

app = Flask(__name__)


@app.route("/")
def hello_world():
  return render_template("index.html")


app.run(host='0.0.0.0', port=8080)
