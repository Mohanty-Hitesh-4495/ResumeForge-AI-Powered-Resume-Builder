import pyrebase
from firebase_config import firebaseConfig, db

# Initialize Pyrebase for authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()