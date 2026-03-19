import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import traceback
import datetime
import sys

from utils import handler

# Initialize Supabase client using environment variables
# Streamlit automatically pulls these from the Linux environment
def get_supabase():
    url = st.secrets.get("url") or os.getenv("url")
    key = st.secrets.get("key") or os.getenv("key")
    if not url or not key:
        # This helps you debug if your 'export' commands didn't work
        raise ValueError(f"Keys found: {list(st.secrets.keys())}. URL env: {os.getenv('URL') is not None}")
    return create_client(url, key)
# Create ONE instance to be used across the whole app
supabase = get_supabase()


def sign_up(email, password):
    try:
        if len(password) < 8:
            return False, "108" # Custom code for short password

        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return True, "Success"
        return False, "500"
        
    except Exception as e:
        handler.log(e, code="201") # Log the nasty technical details
        return False, "201"    # Return the clean code to the UI

def login(email, password):
    """Handles user login via Supabase Auth."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            return True, "Login successful!"
        return False, "Invalid email or password."
    except Exception as e:
        return False, str(e)

def get_current_user_id():
    """Retrieves the secure UUID of the logged-in user."""
    user = supabase.auth.get_user()
    if user:
        return user.user.id
    return None
target_id = get_current_user_id()

# --- auth.py ---
def clear_history():
    target_id = get_current_user_id()
    if not target_id:
        return False, "You are not logged in."
    
    try:
        response = (
            supabase.table("translation_history")
            .delete()
            .eq("user_id", target_id)
            .execute()
        )
        return True, "History cleared successfully!"
    except Exception as e:
        return False, f"Database error: {e}"
