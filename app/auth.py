<<<<<<< HEAD
import pyrebase
from firebase_config import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
=======
import firebase_admin
from firebase_admin import credentials, auth, db, storage
from firebase_config import firebaseConfig
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": firebaseConfig["projectId"],
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
})

# Initialize the app
firebase_admin.initialize_app(cred, {
    'databaseURL': firebaseConfig["databaseURL"],
    'storageBucket': firebaseConfig["storageBucket"]
})

# Get references to services
auth = auth
db = db
storage = storage
>>>>>>> 573db29d34981b8efea90231a1d378da070482c5
