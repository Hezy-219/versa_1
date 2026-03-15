import streamlit as st
import datetime
from auth import supabase # Import the shared supabase client

def show_admin_panel():
    st.divider()
    st.subheader("🛡️ Admin Console")
    
    # 1. Fetch users from Supabase Auth
    # Note: Supabase Admin API is required to list users. 
    # If not using a service role key, you may need a 'profiles' table.
    try:
        # In a real production app, use the Supabase Service Role key 
        # to access auth.users, but for now, let's list from your 'profiles' table
        response = supabase.table("profiles").select("email").execute()
        users = [u['email'] for u in response.data]
    except Exception as e:
        st.error(f"Could not fetch users: {e}")
        return

    if not users:
        st.info("No users found in profiles.")
        return

    target_user = st.selectbox("Select User", users)
    
    # 2. Moderation Logic
    # We now store moderation data in a new 'moderation' table in Supabase
    if st.button(f"🚩 Flag {target_user}"):
        supabase.table("moderation").insert({
            "user_email": target_user,
            "event": "MANUAL_FLAG",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }).execute()
        st.toast(f"Silent flag recorded for {target_user}", icon="📝")

    ban_days = st.number_input("Ban Duration (Days)", 1, 365, 7)
    if st.button(f"🚫 Ban {target_user}"):
        unban_date = (datetime.datetime.utcnow() + datetime.timedelta(days=ban_days)).isoformat()
        
        supabase.table("moderation").upsert({
            "user_email": target_user,
            "status": "banned",
            "unban_date": unban_date
        }).execute()
        st.error(f"User {target_user} banned until {unban_date}")