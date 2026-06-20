import os
from flask import Flask

app = Flask('app')

@app.route('/')
def home():
    return "Neobank Signature is running!"

app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
