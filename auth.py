import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
import random
import string

# --- 1. INITIALIZATION ---
def init_connection():
    """Initializes the Firebase connection securely."""
    if not firebase_admin._apps:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Initialize database client
db = init_connection()

# --- 2. SECURITY HELPERS ---
def hash_password(password):
    """Hashes a password before storing it in the database."""
    # Convert string to bytes, hash it, and convert back to string for database storage
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Checks if the entered password matches the stored hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- 3. CORE AUTHENTICATION LOGIC ---
def authenticate_user(email, password):
    """
    Checks credentials against Firestore.
    Returns: (Boolean success, String message, String role)
    """
    user_ref = db.collection("users").document(email)
    doc = user_ref.get()

    if doc.exists:
        user_data = doc.to_dict()
        
        # Check if the admin blocked this user
        if user_data.get("status") == "Blocked":
            return False, "This account has been blocked. Please contact the administrator.", None
            
        # Verify password
        if verify_password(password, user_data.get("password")):
            return True, "Login successful", user_data.get("role")
        else:
            return False, "Invalid email or password", None
    else:
        return False, "Invalid email or password", None

def create_user(email, password, role="User"):
    """
    Creates a new user in the database.
    Returns: (Boolean success, String message)
    """
    user_ref = db.collection("users").document(email)
    
    if user_ref.get().exists:
        return False, "An account with this email already exists."
        
    user_data = {
        "email": email,
        "password": hash_password(password),
        "role": role,
        "status": "Active" # Defaults to active, admins can change this later
    }
    
    user_ref.set(user_data)
    return True, "User created successfully."

def reset_user_password(email):
    """
    Generates a temporary password, updates the database, and returns the new password.
    Returns: (Boolean success, String temp_password_or_message)
    """
    user_ref = db.collection("users").document(email)
    
    if not user_ref.get().exists:
        return False, "Email not found in the system."
        
    # Generate an 8-character random alphanumeric password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Hash the new temp password and update Firestore
    user_ref.update({
        "password": hash_password(temp_password)
    })
    
    return True, temp_password
