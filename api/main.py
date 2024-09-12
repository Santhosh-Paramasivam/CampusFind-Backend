import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from flask_restful import Api, Resource

service_account_base64 = os.getenv('GOOGLE_CREDENTIALS')
service_account_json = base64.b64decode(service_account_base64).decode('utf-8')
service_account_info = json.loads(service_account_json)

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {"data":service_account_base64}
    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(HelloWorld, "/helloworld")

app = app