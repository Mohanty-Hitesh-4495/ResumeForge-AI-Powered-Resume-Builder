import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import json
import os

# Optional: For local development only
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

def clean_database_url(url: str) -> str:
    """Ensure the Firebase Realtime Database URL is well-formatted."""
    if url:
        url = url.rstrip('/')
        if not url.startswith('https://'):
            url = 'https://' + url
    return url

# --------- Load Firebase Client Config (for Pyrebase) ---------
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY") or st.secrets["firebase_client"]["apiKey"],
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN") or st.secrets["firebase_client"]["authDomain"],
    "projectId": os.getenv("FIREBASE_PROJECT_ID") or st.secrets["firebase_client"]["projectId"],
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") or st.secrets["firebase_client"]["storageBucket"],
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID") or st.secrets["firebase_client"]["messagingSenderId"],
    "appId": os.getenv("FIREBASE_APP_ID") or st.secrets["firebase_client"]["appId"],
    "databaseURL": clean_database_url(os.getenv("FIREBASE_DATABASE_URL") or st.secrets["firebase_client"]["databaseURL"])
}

# --------- Validate required fields ---------
required_vars = [
    "apiKey", "authDomain", "projectId", "storageBucket",
    "messagingSenderId", "appId", "databaseURL"
]
missing_vars = [key for key in required_vars if not firebaseConfig.get(key)]
if missing_vars:
    raise ValueError(f"Missing required Firebase client config fields: {', '.join(missing_vars)}")

# --------- Initialize Firebase Admin SDK (for Firestore) ---------
if not firebase_admin._apps:
    try:
        service_account_info = dict(st.secrets["service_account"])
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {str(e)}")
        raise

# --------- Firestore Client ---------
try:
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firestore client: {str(e)}")
    raise
