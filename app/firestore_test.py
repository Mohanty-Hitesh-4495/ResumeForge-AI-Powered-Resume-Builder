import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client() # connecting to firestore

doc_ref = db.collection("users").document("alovelace")
doc_ref.set({"first": "Hitesh", "last": "Mohanty", "born": 2002})

