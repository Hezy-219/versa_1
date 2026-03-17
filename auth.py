import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import streamlit as st
import traceback
import datetime
import sys

class ErrorHandler:
    def __init__(self, log_file="error.log"):
        self.log_file = log_file

    def log(self, error, code="500"):
        timestamp = datetime.datetime.now()
        trace = traceback.format_exc()
        
        # 1. Write to file (for local testing)
        try:
            with open(self.log_file, "a") as f:
                f.write(f"\n[{timestamp}] ERROR {code}\n{trace}\n---\n")
        except:
            pass 

        # 2. Print to System Console (CRITICAL for Streamlit Cloud Logs)
        # This is what you will see in the black sidebar on the website
        print(f"!!! [{timestamp}] APP ERROR {code} !!!", file=sys.stderr)
        print(trace, file=sys.stderr)

    def respond(self, code="500"):
        messages = {
            "101": "Login failed. Please check your credentials.",
            "201": "Sign-up failed. User may already exist.", # Added for your sign-up flow
            "203": "Translation failed. Try again.",
            "301": "File processing error. Try a smaller file.",
            "603": "Server is currently unavailable. Please retry shortly.",
            "500": "Something went wrong. Please try again."
        }
        st.error(f"{messages.get(code, messages['500'])} (Error {code})")

# Initialize Supabase client using environment variables
# Streamlit automatically pulls these from the Linux environment
def get_supabase():
    url = st.secrets.get("URL") or os.getenv("URL")
    key = st.secrets.get("KEY") or os.getenv("KEY")
    if not url or not key:
        # This helps you debug if your 'export' commands didn't work
        raise ValueError("Sorry we are having problems with our database please try again later, thank you")
    return create_client(url, key)

# Create ONE instance to be used across the whole app
supabase = get_supabase()

err = ErrorHandler()

def sign_up(email, password):
    try:
        if len(password) < 8:
            return False, "108" # Custom code for short password

        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return True, "Success"
        return False, "500"
        
    except Exception as e:
        err.log(e, code="201") # Log the nasty technical details
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
