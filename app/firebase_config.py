import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import json
import streamlit as st

# Load environment variables from .env (for local dev)
load_dotenv()

def clean_database_url(url: str) -> str:
    """Clean and validate the database URL."""
    if not url:
        return url
    url = url.rstrip('/')
    if not url.startswith('https://'):
        url = 'https://' + url
    return url

# Firebase configuration for Pyrebase (from environment or Streamlit secrets)
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY") or st.secrets.get("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN") or st.secrets.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID") or st.secrets.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") or st.secrets.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID") or st.secrets.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID") or st.secrets.get("FIREBASE_APP_ID"),
    "databaseURL": clean_database_url(os.getenv("FIREBASE_DATABASE_URL") or st.secrets.get("FIREBASE_DATABASE_URL"))
}

# Validate required vars
required_vars = [
    "apiKey", "authDomain", "projectId", "storageBucket",
    "messagingSenderId", "appId", "databaseURL"
]
missing_vars = [key for key in required_vars if not firebaseConfig.get(key)]
if missing_vars:
    raise ValueError(f"Missing required Firebase config fields: {', '.join(missing_vars)}")

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # Load service account JSON from Streamlit secrets
        firebase_admin_creds_dict = json.loads(st.secrets["firebase_admin"])

        cred = credentials.Certificate(firebase_admin_creds_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {str(e)}")
        raise

# Initialize Firestore
try:
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firestore client: {str(e)}")
    raise

# Initialize Pyrebase for Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()
