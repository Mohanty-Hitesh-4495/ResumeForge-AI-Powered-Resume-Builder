import streamlit as st
import json
from datetime import datetime
import re
from typing import Optional, Dict, List, Any
import os
from pathlib import Path
from auth import auth, db  # Import Firebase auth and db
from google.cloud.exceptions import NotFound

# --- Firestore Cloud Sync Helpers ---
def save_user_data_firestore(user_id: str, data: dict):
    """Save user data to Firestore."""
    db.collection("users").document(user_id).set(data)

def fetch_user_data_firestore(user_id: str) -> dict:
    """Fetch user data from Firestore."""
    try:
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
    except Exception:
        pass
    return None

# Create data directory structure
DATA_DIR = Path("data")
USER_DATA_DIR = DATA_DIR / "users"
BACKUP_DIR = DATA_DIR / "backups"
TEMP_DIR = DATA_DIR / "temp"

# Create directories if they don't exist
for directory in [DATA_DIR, USER_DATA_DIR, BACKUP_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

def get_user_data_path(user_id: str) -> Path:
    """Get the path for user's data directory"""
    user_dir = USER_DATA_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    return user_dir

def save_user_data(user_id: str, data: Dict[str, Any]) -> str:
    """Save user data to their directory"""
    user_dir = get_user_data_path(user_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_data_{timestamp}.json"
    filepath = user_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)

def load_user_data(user_id: str, filename: str) -> Dict[str, Any]:
    """Load user data from their directory"""
    user_dir = get_user_data_path(user_id)
    filepath = user_dir / filename
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_user_data(user_id: str) -> List[str]:
    """List all data files for a user"""
    user_dir = get_user_data_path(user_id)
    return [f.name for f in user_dir.glob("resume_data_*.json")]

def save_backup(user_id: str, data: Dict[str, Any]) -> str:
    """Save a backup of user data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{user_id}_{timestamp}.json"
    filepath = BACKUP_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)

def load_backup(filename: str) -> Dict[str, Any]:
    """Load data from a backup file"""
    filepath = BACKUP_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_profile_image(user_id: str, image_file, json_filename: str) -> str:
    """Save profile image to user's assets folder"""
    user_dir = get_user_data_path(user_id)
    assets_dir = user_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Get the base name of the JSON file without extension
    base_name = Path(json_filename).stem

    # Save the image with the same base name
    image_path = assets_dir / f"{base_name}{Path(image_file.name).suffix}"

    # Save the image file
    with open(image_path, "wb") as f:
        f.write(image_file.getbuffer())

    return str(image_path)

# Page configuration (This should be the ONLY st.set_page_config call)
st.set_page_config(
    page_title="ResumeForge",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication and data
if 'user' not in st.session_state:
    st.session_state.user = None
if 'show_home' not in st.session_state:
    st.session_state.show_home = True
if 'show_login' not in st.session_state:
    st.session_state.show_login = True
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        'personal_info': {},
        'experience': [],
        'education': [],
        'skills': [],
        'projects': [],
        'certifications': [],
        'languages': []
    }

# Authentication functions
def sign_up(email: str, password: str) -> bool:
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.session_state.user = user
        return True
    except Exception as e:
        st.error(f"Error creating account: {str(e)}")
        return False

def sign_in(email: str, password: str) -> bool:
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        # Fetch Firestore data
        user_id = user['localId']
        firestore_data = fetch_user_data_firestore(user_id)
        if firestore_data:
            st.session_state.resume_data = firestore_data
        return True
    except Exception as e:
        st.error(f"Error signing in: {str(e)}")
        return False

def sign_out():
    st.session_state.user = None
    st.session_state.show_login = True
    st.rerun()

# Authentication UI
if st.session_state.show_login and not st.session_state.user:
    st.markdown("""
    <div class="hero-section">
        <h1>🚀 ResumeForge</h1>
        <p>Create stunning, professional resumes in minutes with our AI-powered builder</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Sign In")
        with st.form("signin_form"):
            signin_email = st.text_input("Email", key="signin_email")
            signin_password = st.text_input("Password", type="password", key="signin_password")
            signin_submitted = st.form_submit_button("Sign In")
            
            if signin_submitted:
                if sign_in(signin_email, signin_password):
                    st.session_state.show_login = False
                    st.rerun()
    
    with col2:
        st.markdown("### 📝 Sign Up")
        with st.form("signup_form"):
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if signup_password != signup_confirm:
                    st.error("Passwords do not match!")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    if sign_up(signup_email, signup_password):
                        st.session_state.show_login = False
                        st.rerun()

    st.stop()  # Stop execution here if not logged in

# Sidebar navigation for main pages
with st.sidebar:
    if st.session_state.user:
        if 'main_page' not in st.session_state:
            st.session_state.main_page = 'resume'  # 'profile', 'resume', 'about'

        # Profile button
        if st.button('👤 Profile'):
            st.session_state.main_page = 'profile'
            user_id = st.session_state.user['localId']
            firestore_data = fetch_user_data_firestore(user_id)
            if firestore_data:
                st.session_state.resume_data = firestore_data

        # Build Resume button
        if st.button('📝 Build Your Resume'):
            st.session_state.main_page = 'resume'

        # About button
        if st.button('ℹ️ About'):
            st.session_state.main_page = 'about'

        # Sign out button
        if st.button('🚪 Sign Out'):
            sign_out()
            st.rerun()

        st.markdown('---')

# Main page rendering
if st.session_state.user:
    if st.session_state.main_page == 'profile':
        personal = st.session_state.resume_data.get('personal_info', {})
        # Custom CSS for profile styling
        st.markdown("""
        <style>
        .profile-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .profile-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .profile-name {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .profile-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .profile-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .info-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 1rem;
            border-radius: 12px;
            border-left: 4px solid #ffffff;
            transition: all 0.3s ease;
        }
        .info-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }
        .info-label {
            font-weight: 600;
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .info-value {
            font-size: 1.1rem;
            font-weight: 500;
            word-break: break-all;
        }
        .profile-image-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        .profile-image {
            border-radius: 50%;
            border: 4px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        .profile-image:hover {
            transform: scale(1.05);
        }
        .summary-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .summary-text {
            font-size: 1.1rem;
            line-height: 1.6;
            font-style: italic;
            text-align: center;
        }
        .no-data {
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
        }
        </style>
        """, unsafe_allow_html=True)
        # Main profile container
        # st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        # Profile header with image and name
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            profile_pic = personal.get('profile_pic', None)
            if profile_pic and os.path.exists(profile_pic):
                st.markdown('<div class="profile-image-container">', unsafe_allow_html=True)
                st.image(profile_pic, width=160, use_column_width=False)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="profile-header">
                <h1 class="profile-name">{personal.get('full_name', 'No Name Provided')}</h1>
            </div>
            """, unsafe_allow_html=True)
        # Contact information grid
        # st.markdown('<div class="info-grid">', unsafe_allow_html=True)
        # Contact details
        contact_info = [
            ("📧 Email", personal.get('email', 'Not provided')),
            ("📱 Phone", personal.get('phone', 'Not provided')),
            ("📍 Location", personal.get('location', 'Not provided')),
            ("💼 LinkedIn", personal.get('linkedin', 'Not provided')),
            ("🐙 GitHub", personal.get('github', 'Not provided'))
        ]
        for label, value in contact_info:
            # Check if it's a URL for LinkedIn/GitHub
            if value != 'Not provided' and ('linkedin.com' in value or 'github.com' in value):
                display_value = f'<a href="{value}" target="_blank" style="color: white; text-decoration: underline;">{value}</a>'
            else:
                display_value = value if value != 'Not provided' else '<span class="no-data">Not provided</span>'
            st.markdown(f"""
            <div class="info-item">
                <div class="info-label">{label}</div>
                <div class="info-value">{display_value}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # Summary section
        summary = personal.get('summary', '')
        if summary and summary.strip():
            st.markdown(f"""
            <div class="summary-section">
                <div class="info-label" style="text-align: center; margin-bottom: 1rem;">✨ PROFESSIONAL SUMMARY</div>
                <div class="summary-text">{summary}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="summary-section">
                <div class="info-label" style="text-align: center; margin-bottom: 1rem;">✨ PROFESSIONAL SUMMARY</div>
                <div class="summary-text no-data">No summary provided yet</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # Add some spacing at the bottom
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    elif st.session_state.main_page == 'about':
        st.markdown('<h2 style="text-align:center;">ℹ️ About</h2>', unsafe_allow_html=True)
        st.info('ResumeForge: Create stunning, professional resumes in minutes with our AI-powered builder!')
    else:
        if 'show_home' in st.session_state and st.session_state.show_home:
            pass
        else:
            pass

# Custom CSS (combined from both files)
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #f44336;
        --text-color: #2c3e50;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header (for both home and form) */
    .main-header {
        background: var(--bg-gradient);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Feature cards (from Home.py) */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid #e1e8ed;
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .feature-card h3 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }

    .feature-card p {
        color: var(--text-color);
        opacity: 0.8;
    }

    /* Action buttons (from Home.py) */
    .action-button {
        background: var(--bg-gradient);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }

    .action-button:hover {
        transform: translateY(-2px);
    }

    /* Section headers (from form.py) */
    .section-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Form styling (from form.py) */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid #e1e8ed;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white !important;
        color: #2c3e50 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white !important;
        color: #2c3e50 !important;
    }

    /* Input placeholder styling (from form.py) */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1;
    }

    /* Button styling (from form.py) */
    .stButton > button {
        border: 1px solid #d3d3d3; /* A subtle border */
        border-radius: 4px; /* Slight curve */
        padding: 0.75rem .5rem; /* Adjust padding */
        background: var(--bg-gradient);
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); /* A more subtle shadow */
        width: 100%; /* Make buttons take full width */
    }
    
    .stButton > button:hover {
        background-color: #e0e0e0; /* Slightly darker on hover */
        border-color: #b0b0b0;
        transform: translateY(-1px);
        box-shadow: 0 3px 7px rgba(0,0,0,0.1);
    }

    /* Cards (from form.py) */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Progress indicator (from form.py) */
    .progress-container {
        background: #f1f3f4;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success message (from form.py) */
    .success-message {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }\n        to { opacity: 1; transform: translateY(0); }\n    }
    
    /* Sidebar styling (from form.py) */
    .css-1d391kg { /* Target sidebar by class */
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white; /* Ensure text in sidebar is readable */
    }

     /* Sidebar links/buttons (from form.py) */
    .css-1d391kg .stButton > button {
        color: #2c3e50; /* Dark text for buttons */
        background: white; /* White background for contrast */
    }

    .css-1d391kg .stButton > button:hover {
        color: white; /* White text on hover */
        background: var(--accent-color); /* Accent color background on hover */
    }

     .css-1d391kg .stMarkdown h3 {
        color: white; /* White text for sidebar headers */
    }

    /* Form sections (from form.py) */
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e8ed;
    }
    
    /* Dynamic list items (from form.py) */
    .dynamic-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid var(--accent-color);
    }

    /* Ensure text is visible in all input fields (from form.py) */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        color: #2c3e50 !important;
        background-color: white !important;
    }

    /* Style for file uploader (from form.py) */
    .stFileUploader > div {
        background: white !important;
        border: 2px solid #e1e8ed !important;
        border-radius: 10px !important;
    }

    /* Style for selectbox options (from form.py) */
    .stSelectbox > div > div > select > option {
        color: #2c3e50 !important;
        background-color: white !important;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); /* Further reduced from 250px */
        gap: 0.8rem; /* Further reduced from 1rem */
        margin: 0 auto;
        padding: 0 0.8rem; /* Reduced from 1rem */
        max-width: 800px;
    }
    .feature-card {
        background: white;
        padding: 1rem; /* Further reduced from 1.2rem */
        border-radius: 8px; /* Further reduced from 10px */
        box-shadow: 0 1px 4px rgba(0,0,0,0.05); /* Further reduced shadow */
        border: 1px solid #e1e8ed;
        transition: all 0.3s ease;
        height: auto;
        min-height: 140px; /* Further reduced from 160px */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
        text-align: left;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .feature-card:hover {
        transform: translateY(-2px); /* Further reduced from -3px */
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); /* Further reduced shadow */
    }
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 0.4rem; /* Further reduced from 0.5rem */
        font-size: 1rem; /* Further reduced from 1.1rem */
        font-weight: 600;
        word-wrap: break-word;
    }
    .feature-card p {
        color: #4a5568;
        opacity: 0.9;
        line-height: 1.3; /* Further reduced from 1.4 */
        font-size: 0.8rem; /* Further reduced from 0.85rem */
        margin-top: 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .feature-icon {
        font-size: 1.6rem; /* Reduced from 2rem */
        margin-bottom: 0.6rem; /* Reduced from 0.8rem */
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .cta-section {
        text-align: center;
        margin: 3rem 0;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .cta-section h2 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    .cta-section p {
        color: var(--text-color);
        opacity: 0.8;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for validation and data management
def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM or YYYY)"""
    if date_str.lower() == 'present':
        return True
    pattern = r'^\d{4}(-\d{2})?$'
    return bool(re.match(pattern, date_str))

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return True
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

def validate_gpa(gpa: str) -> bool:
    """Validate GPA format (0.0-4.0)"""
    if not gpa:
        return True
    try:
        gpa_float = float(gpa)
        return 0.0 <= gpa_float <= 4.0
    except ValueError:
        return False

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate required fields in a dictionary"""
    errors = []
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    return errors

def get_form_completion_percentage() -> float:
    """Calculate form completion percentage"""
    total_fields = 0
    completed_fields = 0

    # Personal Info
    personal_info = st.session_state.resume_data['personal_info']
    required_personal = ['full_name', 'email', 'phone']
    total_fields += len(required_personal)
    completed_fields += sum(1 for field in required_personal if personal_info.get(field))

    # Experience
    experience = st.session_state.resume_data['experience']
    if experience:
        total_fields += 1
        completed_fields += 1

    # Education
    education = st.session_state.resume_data['education']
    if education:
        total_fields += 1
        completed_fields += 1

    # Skills
    skills = st.session_state.resume_data['skills']
    if skills:
        total_fields += 1
        completed_fields += 1

    return (completed_fields / total_fields) * 100 if total_fields > 0 else 0

def auto_save_data():
    """Auto-save resume data to a temporary file"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    # Format timestamp with proper format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = backup_dir / f"resume_backup_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.resume_data, f, indent=2, ensure_ascii=False)

    # Keep only last 5 backups
    backups = sorted(backup_dir.glob("resume_backup_*.json"))
    if len(backups) > 5:
        for old_backup in backups[:-5]:
            old_backup.unlink()

def load_backup(filename: str) -> bool:
    """Load resume data from a backup file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.resume_data = data
        return True
    except Exception as e:
        st.error(f"Error loading backup: {str(e)}")
        return False

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        'personal_info': {},
        'experience': [],
        'education': [],
        'skills': [],
        'projects': [],
        'certifications': [],
        'languages': []
    }

if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Helper functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def save_to_json():
    """Save resume data to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.resume_data, f, indent=2, ensure_ascii=False)
    
    return filename

def save_profile_image(image_file, json_filename):
    """Save profile image to assets folder with matching name"""
    # Create assets directory if it's not exist
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # Get the base name of the JSON file without extension
    base_name = Path(json_filename).stem

    # Save the image with the same base name
    image_path = assets_dir / f"{base_name}{Path(image_file.name).suffix}"

    # Save the image file
    with open(image_path, "wb") as f:
        f.write(image_file.getbuffer())

    return str(image_path)

def load_sample_data():
    """Load sample data for demonstration"""
    st.session_state.resume_data = {
        'personal_info': {
            'full_name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '+1-555-0123',
            'location': 'New York, NY',
            'linkedin': 'linkedin.com/in/johndoe',
            'github': 'github.com/johndoe',
            'summary': 'Experienced software developer with 5+ years in full-stack development...'
        },
        'experience': [
            {
                'company': 'Tech Solutions Inc.',
                'position': 'Senior Developer',
                'start_date': '2022-01',
                'end_date': 'Present',
                'description': 'Led development of web applications using React and Python...'
            }
        ],
        'education': [
            {
                'institution': 'University of Technology',
                'degree': 'Bachelor of Computer Science',
                'year': '2019',
                'gpa': '3.8'
            }
        ],
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
        'projects': [
            {
                'name': 'E-commerce Platform',
                'description': 'Built a full-stack e-commerce platform...',
                'technologies': 'React, Node.js, MongoDB'
            }
        ],
        'certifications': [
            {
                'name': 'AWS Certified Developer',
                'issuer': 'Amazon Web Services',
                'date': '2023-01',
                'credential_id': 'AWS-123456'
            }
        ],
        'languages': [
            {
                'name': 'English',
                'proficiency': 'Native'
            },
            {
                'name': 'Spanish',
                'proficiency': 'Intermediate'
            }
        ]
    }

# Conditional rendering based on session state
if st.session_state.show_home:
    # Enhanced styling
    st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .hero-section {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            padding: 1.5rem; /* Reduced padding */
            border-radius: 12px;
            margin: 0.5rem auto; /* Reduced margin */
            text-align: center;
            color: white;
            box-shadow: 0 4px 12px rgba(106, 17, 203, 0.15);
            max-width: 800px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .hero-section h1 {
            font-size: 2.2rem; /* Slightly reduced font size */
            font-weight: 800;
            margin-bottom: 0.6rem; /* Reduced margin */
        }
        
        .hero-section p {
            font-size: 1rem; /* Slightly reduced font size */
            opacity: 0.9;
            margin: 0;
            line-height: 1.5;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .feature-section {
            padding: 0.5rem; /* Reduced padding */
            background: #f8fafc;
            border-radius: 12px;
            margin: 0.5rem auto; /* Reduced margin */
            max-width: 800px;
            border: 1px solid #e1e8ed;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Adjusted minmax for smaller cards */
            gap: 1rem; /* Reduced gap */
            margin: 0 auto;
            padding: 0 0.5rem; /* Reduced padding */
            max-width: 800px;
        }

        .feature-card {
            background: white;
            padding: 1rem; /* Reduced padding */
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #e1e8ed;
            transition: all 0.3s ease;
            height: auto; /* Keep auto height */
            min-height: 160px; /* Reduced minimum height */
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-start;
            text-align: left;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .feature-icon {
            font-size: 1.8rem; /* Slightly reduced icon size */
            margin-bottom: 0.5rem; /* Reduced margin */
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .feature-card h3 {
            color: #2c3e50;
            margin-bottom: 0.4rem; /* Reduced margin */
            font-size: 1.1rem; /* Slightly reduced font size */
            font-weight: 600;
            word-wrap: break-word;
        }

        .feature-card p {
            color: #4a5568;
            opacity: 0.9;
            line-height: 1.4; /* Slightly reduced line height */
            font-size: 0.85rem; /* Slightly reduced font size */
            margin-top: 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .cta-section {
            text-align: center;
            margin: 0.5rem auto; /* Reduced margin */
            padding: 1rem; /* Reduced padding */
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            max-width: 800px;
            border: 1px solid #e1e8ed;
        }

        .cta-section h2 {
            color: #2c3e50;
            margin-bottom: 0.6rem; /* Reduced margin */
            font-size: 1.6rem; /* Slightly reduced font size */
            font-weight: 600;
        }

        .cta-section p {
            color: #4a5568;
            opacity: 0.9;
            margin-bottom: 1rem; /* Reduced margin */
            font-size: 0.9rem; /* Slightly reduced font size */
            line-height: 1.4; /* Slightly reduced line height */
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .button-container {
            text-align: center;
            margin: 0.5rem 0; /* Reduced margin */
        }

        .start-button {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 0.6rem 1.2rem; /* Adjusted padding to fit text better */
            border-radius: 8px; /* Restored standard border-radius */
            font-size: 0.95rem;
            font-weight: 600; /* Restored correct font weight */
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(106, 17, 203, 0.15);
            width: auto; /* Ensure width fits content */
            /* Removed explicit min/max width to allow shrinking */
            display: inline-block;
        }

        .footer {
            text-align: center;
            margin: 0.5rem auto; /* Reduced margin */
            padding: 0.8rem; /* Reduced padding */
            color: #4a5568;
            font-size: 0.8rem; /* Slightly reduced font size */
            max-width: 800px;
        }

        @media (max-width: 768px) {
            .feature-grid {
                grid-template-columns: 1fr;
                padding: 0 0.5rem;
                gap: 1rem;
            }
            
            .feature-card {
                height: auto;
                min-height: 140px; /* Further reduced min-height on mobile */
                padding: 0.8rem; /* Reduced padding on mobile */
            }

            .feature-icon {
                 font-size: 1.4rem; /* Further reduced icon size on mobile */
                 margin-bottom: 0.4rem;
            }

            .feature-card h3 {
                font-size: 1rem; /* Further reduced font size on mobile */
                margin-bottom: 0.3rem;
            }

            .feature-card p {
                font-size: 0.8rem; /* Further reduced font size on mobile */
            }

            .hero-section, .feature-section, .cta-section, .footer {
                margin: 0.3rem auto; /* Further reduced margins on mobile */
                padding: 1rem; /* Adjusted padding on mobile */
            }

            .hero-section h1 {
                font-size: 1.8rem;
            }
            
            .hero-section p {
                font-size: 0.9rem;
            }

            .cta-section h2 {
                font-size: 1.4rem;
            }

            .cta-section p {
                font-size: 0.85rem;
            }

             .start-button {
                padding: 0.5rem 1rem; /* Adjusted padding on mobile */
                font-size: 0.9rem;
                /* Removed explicit min/max width on mobile */
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1>🚀 ResumeForge</h1>
        <p>Create stunning, professional resumes in minutes with our AI-powered builder</p>
    </div>
    """, unsafe_allow_html=True)

    
    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>Smart Resume Builder</h3>
            <p>Create professional resumes with our intuitive form-based interface. Add your experience, education, skills, and more with ease. Our smart suggestions help you craft the perfect resume.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>Beautiful Templates</h3>
            <p>Choose from multiple professionally designed templates. Each template is optimized for readability and impact, helping you stand out to potential employers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>AI-Powered Suggestions</h3>
            <p>Get intelligent suggestions for your resume content using advanced AI technology. Our AI helps you highlight your strengths and achievements effectively.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>Easy Export</h3>
            <p>Download your resume as a PDF or save your data for future edits. Your information is always safe and accessible, making updates a breeze.</p>
        </div>
        """, unsafe_allow_html=True)
    

    # Enhanced Call to Action section
    # st.markdown("""
    # <div class="cta-section">
    #     <h2>Ready to Create Your Professional Resume?</h2>
    #     <p>Start building your resume now and take the next step in your career journey. Our AI-powered builder will help you create a standout resume in minutes.</p>
    # </div>
    # """, unsafe_allow_html=True)

    # Action button to switch to the form
    st.markdown("""
    <div class="button-container">
    """, unsafe_allow_html=True)

    if st.button("Start Building Your Resume", type="primary", use_container_width=False):
        st.session_state.show_home = False
        st.rerun()

    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

    # Enhanced footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit and Python</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Existing Form Page Content
    st.markdown("""
    <div class="main-header">
        <h1>📝 Resume Builder</h1>
        <p>Fill out your information to create a professional resume</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📋 Resume Sections")
        
        sections = [
            (" Personal Info", 1),
            (" Experience", 2), 
            (" Education", 3),
            (" Skills", 4),
            (" Projects", 5),
            (" Certifications", 6),
            (" Languages", 7),
            (" Export & Save", 8)
        ]
        
        for section_name, step_num in sections:
            if st.button(section_name, key=f"nav_{step_num}"):
                st.session_state.current_step = step_num
        
        st.markdown("---")
        
        # Progress indicator
        completion = get_form_completion_percentage()
        st.markdown("### 📊 Progress")
        st.progress(completion / 100)
        st.markdown(f"**Completion:** {completion:.1f}%")

        # Backup management
        st.markdown("### 💾 Backup Management")

        # List available backups
        backup_dir = Path("backups")
        if backup_dir.exists():
            backups = sorted(backup_dir.glob("resume_backup_*.json"), reverse=True)
            if backups:
                st.markdown("#### Available Backups:")
                for backup in backups[:3]:  # Show last 3 backups
                    try:
                        # Extract timestamp from filename
                        timestamp_str = backup.stem.split('_')[-1]
                        backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        if st.button(f"📅 {backup_time.strftime('%Y-%m-%d %H:%M')}", key=f"load_{backup.name}"):
                            if load_backup(str(backup)):
                                st.success("Backup loaded successfully!")
                                st.rerun()
                    except ValueError:
                        # Skip files with invalid timestamp format
                        continue
            else:
                st.info("No backups available yet")
        
        st.markdown("---")
        
        # Sample data and clear data buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Load Sample Data"):
                load_sample_data()
                st.success("Sample data loaded!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                st.session_state.resume_data = {
                    'personal_info': {},
                    'experience': [],
                    'education': [],
                    'skills': [],
                    'projects': [],
                    'certifications': [],
                    'languages': []
                }
                st.success("Data cleared!")
                st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Step 1: Personal Information
        if st.session_state.current_step == 1:
            st.markdown('<h2 class="section-header">👤 Personal Information</h2>', unsafe_allow_html=True)
            
            with st.container():
                col_a, col_b = st.columns(2)
                
                with col_a:
                    full_name = st.text_input(
                        "Full Name *",
                        value=st.session_state.resume_data['personal_info'].get('full_name', ''),
                        placeholder="Enter your full name",
                        help="Enter your full name as it should appear on your resume"
                    )
                    
                    email = st.text_input(
                        "Email Address *",
                        value=st.session_state.resume_data['personal_info'].get('email', ''),
                        placeholder="your.email@example.com",
                        help="Enter a professional email address"
                    )
                    
                    phone = st.text_input(
                        "Phone Number *",
                        value=st.session_state.resume_data['personal_info'].get('phone', ''),
                        placeholder="+1-555-0123",
                        help="Enter your phone number with country code"
                    )
                
                with col_b:
                    location = st.text_input(
                        "Location",
                        value=st.session_state.resume_data['personal_info'].get('location', ''),
                        placeholder="City, State/Country",
                        help="Enter your current location"
                    )
                    
                    linkedin = st.text_input(
                        "LinkedIn Profile",
                        value=st.session_state.resume_data['personal_info'].get('linkedin', ''),
                        placeholder="linkedin.com/in/yourprofile",
                        help="Enter your LinkedIn profile URL"
                    )
                    
                    github = st.text_input(
                        "GitHub Profile",
                        value=st.session_state.resume_data['personal_info'].get('github', ''),
                        placeholder="github.com/yourusername",
                        help="Enter your GitHub profile URL"
                    )

                # Profile Picture Upload
                profile_pic = st.file_uploader(
                    "Profile Picture (Optional)",
                    type=['jpg', 'jpeg', 'png'],
                    help="Upload a professional profile picture (max 5MB)"
                )

                if profile_pic is not None:
                    if profile_pic.size > 5 * 1024 * 1024:  # 5MB limit
                        st.error("File size too large. Please upload an image smaller than 5MB.")
                    else:
                        # Store the image file in session state temporarily
                        st.session_state.temp_profile_pic = profile_pic
                        st.success("Profile picture uploaded successfully!")

                if st.button("💾 Save Personal Info", type="primary"):
                    errors = []

                    # Validate required fields
                    required_fields = ['full_name', 'email', 'phone']
                    field_values = {
                        'full_name': full_name,
                        'email': email,
                        'phone': phone
                    }
                    errors.extend(validate_required_fields(field_values, required_fields))

                    # Validate email format
                    if email and not validate_email(email):
                        errors.append("Please enter a valid email address")

                    # Validate phone format
                    if phone and not validate_phone(phone):
                        errors.append("Please enter a valid phone number")

                    # Validate URLs
                    if linkedin and not validate_url(linkedin):
                        errors.append("Please enter a valid LinkedIn URL")
                    if github and not validate_url(github):
                        errors.append("Please enter a valid GitHub URL")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # If there's a profile picture, store it temporarily
                        if hasattr(st.session_state, 'temp_profile_pic'):
                            st.session_state.resume_data['personal_info']['temp_profile_pic'] = st.session_state.temp_profile_pic
                            # Clear the temporary profile pic
                            del st.session_state.resume_data['personal_info']['temp_profile_pic']

                        # Update personal info with all data
                        st.session_state.resume_data['personal_info'].update({
                            'full_name': full_name,
                            'email': email,
                            'phone': phone,
                            'location': location,
                            'linkedin': linkedin,
                            'github': github
                        })

                        st.success("✅ Personal information saved successfully!")
                        st.session_state.current_step = 2
                        st.rerun()

        # Step 2: Experience
        elif st.session_state.current_step == 2:
            st.markdown('<h2 class="section-header">💼 Work Experience</h2>', unsafe_allow_html=True)
            
            # Display existing experiences
            for i, exp in enumerate(st.session_state.resume_data['experience']):
                with st.expander(f"📍 {exp.get('position', 'Position')} at {exp.get('company', 'Company')}", expanded=False):
                    st.write(f"**Duration:** {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
                    st.write(f"**Description:** {exp.get('description', 'N/A')}")
                    if st.button(f"🗑️ Remove", key=f"remove_exp_{i}"):
                        st.session_state.resume_data['experience'].pop(i)
                        st.rerun()
            
            # Add new experience
            with st.container():
                st.markdown("#### ➕ Add New Experience")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    company = st.text_input("Company Name *", key="new_company")
                    position = st.text_input("Position/Title *", key="new_position")
                
                with col_b:
                    start_date = st.text_input("Start Date *", placeholder="YYYY-MM or YYYY", key="new_start_date")
                    end_date = st.text_input("End Date", placeholder="YYYY-MM, YYYY, or 'Present'", key="new_end_date")
                
                description = st.text_area("Job Description *", 
                                         placeholder="Describe your responsibilities and achievements...",
                                         height=100, key="new_description")
                
                if st.button("➕ Add Experience", type="primary"):
                    if company and position and start_date:
                        new_exp = {
                            'company': company,
                            'position': position,
                            'start_date': start_date,
                            'end_date': end_date or 'Present',
                            'description': description
                        }
                        st.session_state.resume_data['experience'].append(new_exp)
                        st.success("✅ Experience added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")

        # Step 3: Education
        elif st.session_state.current_step == 3:
            st.markdown('<h2 class="section-header">🎓 Education</h2>', unsafe_allow_html=True)
            
            # Display existing education
            for i, edu in enumerate(st.session_state.resume_data['education']):
                with st.expander(f"🏫 {edu.get('degree', 'Degree')} - {edu.get('institution', 'Institution')}", expanded=False):
                    st.write(f"**Year:** {edu.get('year', 'N/A')}")
                    if edu.get('gpa'):
                        st.write(f"**GPA:** {edu.get('gpa')}")
                    if st.button(f"🗑️ Remove", key=f"remove_edu_{i}"):
                        st.session_state.resume_data['education'].pop(i)
                        st.rerun()
            
            # Add new education
            with st.container():
                st.markdown("#### ➕ Add New Education")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    institution = st.text_input("Institution Name *", key="new_institution")
                    degree = st.text_input("Degree/Certification *", key="new_degree")
                
                with col_b:
                    year = st.text_input("Graduation Year *", placeholder="YYYY", key="new_year")
                    gpa = st.text_input("GPA (Optional)", placeholder="3.8/4.0", key="new_gpa")
                
                if st.button("➕ Add Education", type="primary"):
                    if institution and degree and year:
                        new_edu = {
                            'institution': institution,
                            'degree': degree,
                            'year': year,
                            'gpa': gpa
                        }
                        st.session_state.resume_data['education'].append(new_edu)
                        st.success("✅ Education added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")

        # Step 4: Skills
        elif st.session_state.current_step == 4:
            st.markdown('<h2 class="section-header">🛠️ Skills</h2>', unsafe_allow_html=True)
            
            with st.container():
                # Display current skills
                if st.session_state.resume_data['skills']:
                    st.markdown("#### Current Skills:")
                    # Create a single row of skills with delete buttons
                    for i, skill in enumerate(st.session_state.resume_data['skills']):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"🔹 {skill}")
                        with col2:
                            if st.button(f"🗑️ Remove", key=f"remove_skill_{i}"):
                                st.session_state.resume_data['skills'].pop(i)
                                st.rerun()
                
                # Add new skill
                st.markdown("#### ➕ Add New Skill")
                new_skill = st.text_input(
                    "Skill Name",
                    placeholder="e.g., Python, Project Management, Data Analysis",
                    key="new_skill"
                )

                col_add, col_bulk = st.columns(2)
                with col_add:
                    if st.button("➕ Add Skill", type="primary"):
                        if new_skill and new_skill not in st.session_state.resume_data['skills']:
                            st.session_state.resume_data['skills'].append(new_skill)
                            st.success("✅ Skill added!")
                            st.rerun()
                        elif new_skill in st.session_state.resume_data['skills']:
                            st.warning("Skill already exists!")
                
                with col_bulk:
                    if st.button("📝 Bulk Add Skills"):
                        bulk_skills = st.text_area(
                            "Enter skills separated by commas:",
                            placeholder="Python, JavaScript, SQL, React, Node.js",
                            key="bulk_skills"
                        )
                        if bulk_skills:
                            skills_list = [skill.strip() for skill in bulk_skills.split(',') if skill.strip()]
                            for skill in skills_list:
                                if skill not in st.session_state.resume_data['skills']:
                                    st.session_state.resume_data['skills'].append(skill)
                                st.success(f"✅ Added {len(skills_list)} skills!")
                                st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # Step 5: Projects
        elif st.session_state.current_step == 5:
            st.markdown('<h2 class="section-header">🚀 Projects</h2>', unsafe_allow_html=True)
            
            # Display existing projects
            for i, project in enumerate(st.session_state.resume_data['projects']):
                with st.expander(f"🔧 {project.get('name', 'Project Name')}", expanded=False):
                    st.write(f"**Description:** {project.get('description', 'N/A')}")
                    st.write(f"**Technologies:** {project.get('technologies', 'N/A')}")
                    if project.get('url'):
                        st.write(f"**URL:** {project.get('url')}")
                    if st.button(f"🗑️ Remove", key=f"remove_project_{i}"):
                        st.session_state.resume_data['projects'].pop(i)
                        st.rerun()
            
            # Add new project
            with st.container():
                st.markdown("#### ➕ Add New Project")
                
                project_name = st.text_input("Project Name *", key="new_project_name")
                project_desc = st.text_area("Project Description *", 
                                           placeholder="Describe what the project does and your role...",
                                           height=100, key="new_project_desc")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    technologies = st.text_input("Technologies Used *", 
                                                   placeholder="React, Node.js, MongoDB", key="new_technologies")
                with col_b:
                    project_url = st.text_input("Project URL (Optional)", 
                                                  placeholder="https://github.com/...", key="new_project_url")
                
                if st.button("➕ Add Project", type="primary"):
                    if project_name and technologies:
                        new_project = {
                            'name': project_name,
                            'description': project_desc,
                            'technologies': technologies,
                            'url': project_url
                        }
                        st.session_state.resume_data['projects'].append(new_project)
                        st.success("✅ Project added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")

        # Step 6: Certifications
        elif st.session_state.current_step == 6:
            st.markdown('<h2 class="section-header">📜 Certifications</h2>', unsafe_allow_html=True)
            
            # Display existing certifications
            for i, cert in enumerate(st.session_state.resume_data['certifications']):
                with st.expander(f"🏅 {cert.get('name', 'Certification')}", expanded=False):
                    st.write(f"**Issuer:** {cert.get('issuer', 'N/A')}")
                    st.write(f"**Date:** {cert.get('date', 'N/A')}")
                    if cert.get('credential_id'):
                        st.write(f"**Credential ID:** {cert.get('credential_id')}")
                    if st.button(f"🗑️ Remove", key=f"remove_cert_{i}"):
                        st.session_state.resume_data['certifications'].pop(i)
                        st.rerun()
            
            # Add new certification
            with st.container():
                st.markdown("#### ➕ Add New Certification")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    cert_name = st.text_input("Certification Name *", key="new_cert_name")
                    issuer = st.text_input("Issuing Organization *", key="new_issuer")
                
                with col_b:
                    cert_date = st.text_input("Date Obtained *", placeholder="YYYY-MM", key="new_cert_date")
                    credential_id = st.text_input("Credential ID (Optional)", key="new_credential_id")
                
                if st.button("➕ Add Certification", type="primary"):
                    if cert_name and issuer and cert_date:
                        new_cert = {
                            'name': cert_name,
                            'issuer': issuer,
                            'date': cert_date,
                            'credential_id': credential_id
                        }
                        st.session_state.resume_data['certifications'].append(new_cert)
                        st.success("✅ Certification added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")

        # Step 7: Languages
        elif st.session_state.current_step == 7:
            st.markdown('<h2 class="section-header">🌍 Languages</h2>', unsafe_allow_html=True)
            
            # Display existing languages
            for i, lang in enumerate(st.session_state.resume_data['languages']):
                with st.expander(f"🌐 {lang.get('name', 'Language')}", expanded=False):
                    st.write(f"**Proficiency:** {lang.get('proficiency', 'N/A')}")
                    if st.button(f"🗑️ Remove", key=f"remove_lang_{i}"):
                        st.session_state.resume_data['languages'].pop(i)
                        st.rerun()
            
            # Add new language
            with st.container():
                st.markdown("#### ➕ Add New Language")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    lang_name = st.text_input("Language *", key="new_lang_name")
                
                with col_b:
                    proficiency = st.selectbox("Proficiency Level *", 
                                             ["Native", "Fluent", "Advanced", "Intermediate", "Basic"],
                                             key="new_proficiency")
                
                if st.button("➕ Add Language", type="primary"):
                    if lang_name:
                        new_lang = {
                            'name': lang_name,
                            'proficiency': proficiency
                        }
                        st.session_state.resume_data['languages'].append(new_lang)
                        st.success("✅ Language added successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a language name")

        # Step 8: Export & Save
        elif st.session_state.current_step == 8:
            st.markdown('<h2 class="section-header">📥 Export & Save</h2>', unsafe_allow_html=True)
            
            with st.container():
                # Data completeness check
                completeness = []
                if st.session_state.resume_data['personal_info'].get('full_name'):
                    completeness.append("✅ Personal Information")
                else:
                    completeness.append("❌ Personal Information")
                
                if st.session_state.resume_data['experience']:
                    completeness.append("✅ Work Experience")
                else:
                    completeness.append("⚠️ Work Experience (Optional)")
                
                if st.session_state.resume_data['education']:
                    completeness.append("✅ Education")
                else:
                    completeness.append("⚠️ Education (Optional)")
                
                if st.session_state.resume_data['skills']:
                    completeness.append("✅ Skills")
                else:
                    completeness.append("⚠️ Skills (Recommended)")
                
                st.markdown("#### 📊 Resume Completeness:")
                for item in completeness:
                    st.markdown(f"- {item}")
                
                st.markdown("---")
                
                # Export options
                col_json, col_preview = st.columns(2)
                
                with col_json:
                    if st.button("💾 Save Resume", type="primary"):
                        try:
                            if st.session_state.user:
                                user_id = st.session_state.user['localId']
                                
                                # Handle profile picture if exists
                                if 'temp_profile_pic' in st.session_state.resume_data['personal_info']:
                                    image_path = save_profile_image(
                                        user_id,
                                        st.session_state.resume_data['personal_info']['temp_profile_pic'],
                                        f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                    )
                                    st.session_state.resume_data['personal_info']['profile_pic'] = image_path
                                    del st.session_state.resume_data['personal_info']['temp_profile_pic']

                                # Save the resume data
                                filepath = save_user_data(user_id, st.session_state.resume_data)
                                
                                # Create a backup
                                save_backup(user_id, st.session_state.resume_data)

                                # Save to Firestore
                                save_user_data_firestore(user_id, st.session_state.resume_data)

                                st.markdown(f"""
                                <div class="success-message">
                                    <h4>🎉 Success!</h4>
                                    <p>Resume data saved successfully!</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Provide download link
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    json_data = f.read()
                                
                                st.download_button(
                                    label="📥 Download JSON File",
                                    data=json_data,
                                    file_name=Path(filepath).name,
                                    mime="application/json"
                                )
                            else:
                                st.error("Please sign in to save your resume data")
                        except Exception as e:
                            st.error(f"Error saving file: {str(e)}")
                
                with col_preview:
                    if st.button("👁️ Preview JSON Data"):
                        st.json(st.session_state.resume_data)

    # Template Selection and Resume Generation Section
    st.markdown("---")
    st.markdown('<h2 class="section-header">📄 Resume Generation</h2>', unsafe_allow_html=True)

    # Import the resume generator
    from resume_generator import ResumeGenerator, show_resume_preview

    # Initialize generator
    generator = ResumeGenerator()

    # Create a single column for template selection and controls
    st.markdown("#### 🎨 Choose Template")

    # Template selection with preview cards
    template_name = st.radio(
        "Select a template style:",
        options=list(generator.templates.keys()),
        format_func=lambda x: x.capitalize(),
        label_visibility="collapsed"
    )

    # Template descriptions
    template_descriptions = {
        "classic": "Traditional two-column layout with a professional look",
        "modern": "Contemporary design with a bold header and card-based sections",
        "minimalist": "Clean and simple layout focusing on content"
    }

    st.markdown(f"**{template_name.capitalize()} Style**")
    st.markdown(f"_{template_descriptions[template_name]}_")

    # Create a container for the generate and download buttons
    button_container = st.container()
    with button_container:
        col_gen, col_dl = st.columns(2)
        with col_gen:
            generate_clicked = st.button("🔄 Generate Resume", type="primary", use_container_width=True)
        with col_dl:
            download_disabled = 'last_generated_resume' not in st.session_state
            download_clicked = st.button("📥 Download PDF", disabled=download_disabled, use_container_width=True)

    if generate_clicked:
        with st.spinner("Generating your resume..."):
            from summarizer_agent import generate_profile_summary, generate_project_description, generate_job_description

            # Generate profile summary
            if st.session_state.resume_data['personal_info']:
                personal_info = st.session_state.resume_data['personal_info']
                personal_info['summary'] = generate_profile_summary(personal_info)

            # Generate project descriptions
            for project in st.session_state.resume_data['projects']:
                if not project.get('description'):
                    project['description'] = generate_project_description(
                        project['name'],
                        project['technologies'].split(', ')
                    )

            # Generate job descriptions
            for exp in st.session_state.resume_data['experience']:
                if not exp.get('description'):
                    exp['description'] = generate_job_description(
                        exp['company'],
                        exp['position'],
                        exp['start_date'],
                        exp['end_date']
                    )

            # Generate the resume preview
            show_resume_preview(generator, template_name, st.session_state.resume_data)

            # Generate the PDF and store in session state
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"resume_{timestamp}.pdf"
            pdf_path = generator.generate_pdf(
                generator.render_template(template_name, st.session_state.resume_data),
                pdf_filename
            )
            if pdf_path:
                pdf_bytes, download_filename = generator.get_pdf_download_link(pdf_path)
                if pdf_bytes:
                    st.session_state.generated_pdf_bytes = pdf_bytes
                    st.session_state.generated_pdf_filename = download_filename
                else:
                    st.session_state.generated_pdf_bytes = None
                    st.session_state.generated_pdf_filename = None
            else:
                st.session_state.generated_pdf_bytes = None
                st.session_state.generated_pdf_filename = None

            st.success("✅ Resume generated successfully! You can now download the PDF.")

    # Show download button if PDF is available
    if st.session_state.get('generated_pdf_bytes'):
        st.download_button(
            label="📥 Download PDF",
            data=st.session_state.generated_pdf_bytes,
            file_name=st.session_state.generated_pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )