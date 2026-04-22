# utils.py
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
        # Print to Streamlit Cloud console
        print(f"!!! [{timestamp}] ERROR {code} !!!\n{trace}", file=sys.stderr)

    def respond(self, code="500"):
        messages = {
            "101": "Login failed. Check your credentials.",
            "108": "Password too short (min 8 characters).",
            "201": "Sign-up failed. User may already exist.",
            "203": "Translation failed. Try again.",
            "500": "Something went wrong. USually this doesn't affect page so ignore it however if does, Please try again."
        }
        st.error(f"{messages.get(code, messages['500'])} (Error {code})")

# Create ONE instance to use everywhere
handler = ErrorHandler()
