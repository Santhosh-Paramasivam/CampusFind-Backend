import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from flask_restful import Api, Resource

service_account_base64 = os.getenv('FIREBASE_AUTH_CREDENTIALS')
service_account_json = base64.b64decode(service_account_base64).decode('utf-8')
service_account_info = json.loads(service_account_json)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

app = Flask(__name__)
api = Api(app)

API_KEY = "klXJfkUSyMFuIevkzCDJ7cn5uUzrFCyT"

def apiKeyCheck(req):
    # Step 2: Debug the headers to ensure the API key is sent
    api_key = req.headers.get('x-api-key')
        
    return api_key == API_KEY

def updateDocument(collection_id, query, updated_values):

    collection_ref = db.collection(collection_id)

    # Query for documents where user_id equals 1
    query_ref = collection_ref.where(query[0],query[1],query[2])
    docs = query_ref.stream()

    # Initialize a counter to track how many documents are updated
    doc_updated = False

    # Loop through all documents found in the query
    for doc in docs:
        doc_ref = db.collection(collection_id).document(doc.id)

        # Update the user_id in the found document
        doc_ref.update(updated_values)
        doc_updated = True  # Increment the counter after each update

    # Check if any documents were updated and return a message accordingly
    return doc_updated

class getUserFromUID(Resource):
    def get(self):
        collection_ref = db.collection('rfid_users')

        query_ref = collection_ref.where("rfid", "==", "AAAAAAAA")
        docs = query_ref.stream()

        docs_list = list(docs)
        if docs_list:
            doc = docs_list[0]
            return {
                "id": doc.id,
                "user_id": doc.to_dict().get('user_id')
            }
        else:
            return {"error": "No matching document found"}, 404
        
class getRoomFromMACAddress(Resource):
    def get(self):
        collection_ref = db.collection('rfid_reader_location')

        query_ref = collection_ref.where("reader_mac_address", "==", "1234")
        docs = query_ref.stream()

        docs_list = list(docs)
        if docs_list:
            doc = docs_list[0]
            return {
                "id": doc.id,
                "location": doc.to_dict().get('location')
            }
        else:
            return {"error": "No matching document found"}, 404

class updateUserLocation(Resource):
    def post(self):
        if not apiKeyCheck(request):
            return {"Error":"Unauthorised access"},401
        else:
            return {"success":"Authenticated"},200
        #data = request.json
        
        #if not data:
        #    return {"Error":"no input data sent"},400
        #if 'uid' not in data:
        #    return {"Error":"uid field not sent"},400
        #if 'mac_address' not in data:
        #    return {"Error":"mac_address field not sent"},400    
        
        #if not updateDocument('rfid_users',('user_id','==',1),{"user_id":2}):
        #   return {"Error":"User document not updated"}, 400
        #else:
        #    return {"Success":"User document updated"}, 200
        
            
class sendScannedUID(Resource):
    def get(self):
        if not apiKeyCheck(request):
            return {"error": "Unauthorized access"}, 401
        
        data = request.json
        if not data:
            return {"error": "Bad Request, No data in request"}, 400
        if 'uid' not in data:
            return {"error": "Bad Request, Tag uid not in request"}, 400
        if 'mac_address' not in data:
            return {"error": "Bad Request, MAC Address not in request"}, 400
        
        return data, 200

    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(getUserFromUID, "/getUserFromUID")
api.add_resource(getRoomFromMACAddress, "/getRoomFromMACAddress")
api.add_resource(sendScannedUID,  "/track_update")
api.add_resource(updateUserLocation,"/update_user_location")

app = app