import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

# Load environment variables from .env file
load_dotenv()

def clean_database_url(url: str) -> str:
    """Clean and validate the database URL."""
    if not url:
        return url
    # Remove trailing slash if present
    url = url.rstrip('/')
    # Ensure URL starts with https://
    if not url.startswith('https://'):
        url = 'https://' + url
    return url

# Firebase configuration using environment variables
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")  # Required by Pyrebase
}

# Validate that all required environment variables are set
required_vars = [
    "FIREBASE_API_KEY",
    "FIREBASE_AUTH_DOMAIN",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_STORAGE_BUCKET",
    "FIREBASE_MESSAGING_SENDER_ID",
    "FIREBASE_APP_ID",
    "FIREBASE_DATABASE_URL"  # Added back to required vars
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize Firebase Admin SDK only if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {str(e)}")
        raise

# Initialize Firestore client
try:
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firestore client: {str(e)}")
    raise

# Initialize Pyrebase for authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()
