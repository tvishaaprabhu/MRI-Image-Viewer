import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
# import bcrypt
import random
import string

# --- 1. INITIALIZATION ---
def init_connection():
    if not len(firebase_admin._apps):
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_connection()

# --- 2. SECURITY HELPERS ---
def hash_password(password):
    # hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # return hashed_bytes.decode('utf-8')
    return password  # plain text for now

def verify_password(plain_password, stored_password):
    # return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
    return plain_password == stored_password  # plain text comparison for now

# --- 3. CORE AUTHENTICATION LOGIC ---
def authenticate_user(email, password):
    user_ref = db.collection("users").document(email)
    doc = user_ref.get()

    if doc.exists:
        user_data = doc.to_dict()

        if user_data.get("status") == "Blocked":
            return False, "This account has been blocked. Please contact the administrator.", None

        if verify_password(password, user_data.get("password")):
            return True, "Login successful", user_data.get("role")
        else:
            return False, "Invalid email or password", None
    else:
        return False, "Invalid email or password", None

def create_user(email, password, role="User"):
    user_ref = db.collection("users").document(email)

    if user_ref.get().exists:
        return False, "An account with this email already exists."

    user_data = {
        "email": email,
        "password": hash_password(password),
        "role": role,
        "status": "Active"
    }

    user_ref.set(user_data)
    return True, "User created successfully."

def reset_user_password(email):
    user_ref = db.collection("users").document(email)

    if not user_ref.get().exists:
        return False, "Email not found in the system."

    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    user_ref.update({
        "password": hash_password(temp_password)
    })

    return True, temp_password
