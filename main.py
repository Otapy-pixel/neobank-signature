import os
from flask import Flask

app = Flask('app')

@app.route('/')
def home():
    return "Neobank Signature is running!"
