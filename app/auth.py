import pyrebase
from firebase_config import firebaseConfig, db

# Initialize Pyrebase App
firebase = pyrebase.initialize_app(firebaseConfig)

# Firebase Authentication and Storage (from Pyrebase)
auth = firebase.auth()
storage = firebase.storage()
