import os
import json
from flask import Flask, render_template

app = Flask(__name__)
api_key = os.environ.get('api_key')

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
