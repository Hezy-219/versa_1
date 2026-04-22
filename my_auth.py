import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import traceback
import datetime
import sys

from my_utils import handler

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


def sign_up_user(email, password):
    try:
        res = supabase.auth.sign_up({
            "email": email, 
            "password": password
        })
        
        # Supabase returns the user object on success
        if res.user:
            return True, "Sign-up successful! Please check your email for a confirmation link."
        
        # If res.user is somehow None but no exception was raised
        return False, "Sign-up failed: Unknown error."

    except Exception as e:
        # Log the error for your internal tracking
        handler.log(f"Error during sign-up: {str(e)}", code="201")
        
        # Return a clean error message to the UI
        # We strip the error message to keep it user-friendly
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "This email is already registered."
        
        return False, f"Sign-up failed: {error_msg}"

def login(email, password):
    """Handles user login via Supabase Auth."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        
        if response.user:
            return True, "Login successful!"
        
        # If the code reaches here, Supabase didn't throw an error 
        # but didn't return a user (rare, but keeps the return consistent)
        return False, "Login failed: No user found."

    except Exception as e:
        # Your custom logger handles the dirty work
        handler.log(f"Login failed for {email}: {str(e)}", code='101')
        
        # We still return False + the error string so main.py 
        # success, msg = login(...) can execute safely.
        return False, str(e),

    except Exception as e:
        # Your custom logger handles the dirty work
        handler.log(f"Login failed for {email}: {str(e)}", code='101')
        
        # We still return False + the error string so main.py 
        # success, msg = login(...) can execute safely.
        return False, str(e)
def get_current_user_id():
    """Retrieves the UUID, checking session state first to bypass Streamlit's 'amnesia'."""
    # Check if we already saved it in this session
    if 'user_id' in st.session_state and st.session_state['user_id']:
        return st.session_state['user_id']
    
    # If not in state, try to get it from the Supabase client
    try:
        res = supabase.auth.get_user()
        if res and res.user:
            # Save it to state immediately for the next rerun
            st.session_state['user_id'] = res.user.id
            return res.user.id
    except Exception:
        pass
        
    return None

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
        return False, f"Database error"
