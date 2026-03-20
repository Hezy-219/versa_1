import streamlit as st
from deep_translator import GoogleTranslator
import time
import random
import os
from PIL import Image
import supabase

# Import your optimized auth.py and admin panel
# In main.py
from auth import login, sign_up_user, get_current_user_id, supabase, clear_history
from admin import show_admin_panel
from utils import handler



# --- CONFIGURATION ---
# Use a relative path so it works in any environment (Linux/Cloud)


# Get the directory of your script
# --- CONFIGURATION ---
# No more Image.open(), no more file path issues
st.write("Updated version deployed successfully. Enjoy seamless translations!")
try: 
    st.set_page_config(
        page_title="VersaTranslate", 
        page_icon="🌐", 
        layout="centered"
    )
    
    
    # --- RANDOM LOGIN WORDS ---
    words = {i: msg for i, msg in enumerate([
        "Welcome!!!", "Bienvenue!!!", "Bienvenido", "Willkommen", "いらっしゃいませ",
        "مرحباً", "欢迎", "歡迎", "환영", "Добро пожаловать", "Boas-vindas",
        "Benvenuto", "Welkom", "स्वागत", "Hoş geldin!", "Chào mừng", 
        "Croeso", "Wamkelekile", "Kaabo", "Wamukelekile", "Dobrodošli"
    ], 1)}
    language_options = {
        "French": "fr", "English": "en", "Spanish": "es", "Latin": "la", "German": "de", "Japanese": "ja", 
        "Arabic": "ar", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW", "Korean": "ko",
        "Russian": "ru", "Portuguese": "pt", "Italian": "it", "Dutch": "nl", 'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'iw',
        "Hindi": "hi", "Turkish": "tr", "Vietnamese": "vi",
        "Welsh": "cy", "Xhosa": "xh", "Yoruba": "yo", 'igbo': 'ig', "Zulu": "zu"
    }
    # --- AUTH UI ---
    # --- main.py ---
    import streamlit as st
    from auth import sign_up_user, login  # Ensure these are imported from your auth.py
    
    # 1. ALWAYS initialize session state at the very top
    if 'authenticated' not in st.session_state:
        st.session_state.update({'authenticated': False, 'user_email': None})
    
    # 2. Authentication Block
    if not st.session_state['authenticated']:
        st.title("🔐 Login to VersaTranslate")
        
        # Using a container helps keep the layout organized and prevents rendering bugs
        with st.container():
            auth_mode = st.radio("Choose:", ["Login", "Sign Up"])
            
            # These are your input widgets
            email = st.text_input("Username (Email)")
            password = st.text_input(
                "Password", 
                type="password", 
                help="Must be 8+ characters including letters, numbers, and symbols."
            )
    
            if st.button("Submit"):
                if auth_mode == "Sign Up":
                    success, msg = sign_up_user(email, password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(f"Error: {handler.respond(code='201')}")
                else:
                    success, msg = login(email, password)
                    if success:
                        st.session_state.update({'authenticated': True, 'user_email': email})
                        st.rerun()  # Forces the app to refresh and show the main app
                    else:
                        st.error("Sorry server seems too be encountering errors")
        
        # 3. Stop rendering the rest of the file here
        st.stop()
    
    # --- Everything below this line is the main app (hidden until auth) ---
    
    # --- AGREEMENT ---
    if not st.session_state.get("Agree", False):
        with st.expander("Notice/Agreements"):
            st.write("We don't collect your data to train our systems. All rights reserved. We are not affilated with any organizations and futhermore aren't liable to errors within app. By using our app you agree to allowing app to view files you explicitly share.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes"):
                    st.session_state["Agree"] = True
                    st.rerun()
            with col2:
                if st.button("No"):
                    st.session_state['authenticated'] = False
                    st.rerun()
        st.stop()
    
    # --- LOGIC ---
    def event():
        if st.session_state.get("run_words"):
            n = random.randint(1, 21)
            st.toast(f"🎉 {words.get(n)}", icon="👋")
            st.session_state["run_words"] = False
    
    st.title("🌐 VersaTranslate")
    event()
    def process_parallel_variables(text, code, name, total, limit=4000):
        try:
            # Split the original into a list of chunks
            original_chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
            translated_chunks = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, chunk in enumerate(original_chunks):
                status_text.text(f"Processing segment {i+1} of {len(original_chunks)}...")
                
                
                # 1. Translate the chunk
                t_chunk = perform_translation_chunk(chunk, code) 
                translated_chunks.append(t_chunk)
                
                # 2. Update Progress
                progress_bar.progress((i + 1) / len(original_chunks))
                
            # 3. Concatenate everything at the end
            final_original = "".join(original_chunks)
            final_translated = "".join(translated_chunks)
            # Instead of save_to_supabase(full_orig, full_trans):
            st.divider()
            st.success("Translation complete!")
        
        # Prepare the data for download
    
            st.download_button(
                    label="Download Translation",
                    data=final_translated,
                    file_name=f"Versatranslate_v1_demo_{name}",
                    mime="text/plain"
            )
        except Exception as e:
            st.stop
            st.write("An error occured. Try again later")
    
    def perform_translation_chunk(text, target_lang):
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translated_text
        except Exception as e:
            return "An error ocurred during translation"
    
    
    # --- NEW SUPABASE TRANSLATION LOGIC ---
    def perform_translation(text, target_lang):
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
            user_id = get_current_user_id()
            
            # Save to Supabase 'translation_history' table
            supabase.table("translation_history").insert({
                "user_id": user_id,
                "input_text": text,
                "output_text": translated_text,
                "target_lang": target_lang
            }).execute()
            
            return translated_text
        except Exception as e:
            return "An error ocurred during translation"
    
    # --- SIDEBAR & HISTORY (Updated for Supabase) ---
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state['user_email']}")
    
        # --- ADMIN PANEL GATED ACCESS ---
        # Replace with your email to access admin tools
        if st.session_state['user_email'] == "irekiigbeayoolorunnimi@gmail.com":
            show_admin_panel()
    
        st.divider()
        st.header("Settings")
        selected_lang_name = st.selectbox("Choose Target Language:", options=list(language_options.keys()))
        target_lang_code = language_options[selected_lang_name]

        st.divider()
        with st.expander("About us"):
            st.write("We are company named Silktorch founded in Canada, this app is made to ease the worries of translation offering text uploads and our very own file upload doesn't sound special right but it works! Contact us at vulnerability.report.maximillian@gmail.com . We are open to suggestions and we strive to respond to your emails within a minimum of 48 hours and a maximum of a week(don't worry, this has never happened).Thank you for using our app. NOTE: complaints are treated as suggestions.")

        st.divider()
        with st.expander("Contact us"):
            st.write("You can contact us at vulnerability.report.maximillian@gmail.com, we are open to any of your suggestionsand we will respond as soon as possible specifically by 48 hours")

        st.divider()
        with st.expander("Purpose"):
            st.write("This application is created to gain the trust for our other updates and other apps in work.")

        st.divider()
        with st.expander("Expected Updates"):
            st.write("Due to a possible constriction in resources, app may go through changes, we will try as much as possible to maintain how it is right now but you may expect a possible phase of commercialization (Pro tier and an inclusive free tier), we are also testing a beta feature to ensure graceful failures(we will present games incase of errors that may occur in servers or games, NOTE: This is a beta feature and won't be added until it is ready). Our plans or expectations may change at any point.")
        
        st.divider()
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user_email'] = None
            st.rerun()
        st.divider()
        st.write("Versions supported: v1.0.1")
    
    mode = st.radio("Choose Translation Method:", ["Text Input", "File Upload"], horizontal=True)
    
    if mode == "Text Input":
        st.subheader(f"Translate to {selected_lang_name}")
        eng_text = st.text_area("Enter text to translate:", height=150)
    
        if st.button("Translate 🚀"):
            if eng_text:
                with st.spinner(f"Translating to {selected_lang_name}..."):
                    time.sleep(0.3)
                    result = perform_translation(eng_text, target_lang_code)
                    st.subheader("Result:")
                    st.success(result)
                    st.caption("Translation errors may occur")
            else:
                st.warning("Please enter some text.")
    else:
        # --- FILE UPLOAD LOGIC ---
        st.subheader(f"Translate .txt File to {selected_lang_name}")
        uploaded_file = st.file_uploader("Choose a TXT file", type="txt", help="Max size: 5MB")
    
        if uploaded_file is not None:
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("❌ File is too large. Please upload a file under 5MB.")
            else:
                file_content = uploaded_file.getvalue().decode("utf-8")
                if len(file_content) > 4000:
                        st.warning("❌ File content exceeds 4000 characters.Chunking and splitting might solve this but Chunking isn't stable i.e Chunking might not always work also most features would be deactivated to ensure stability during chunking.")
                        with st.expander("Do wish to perform chunking?"):
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Yes"):
                                    with st.spinner("Hold on"):
                                        total = len(file_content)
                                        st.write(f"Total words: {total}")
                                        process_parallel_variables(file_content, target_lang_code, uploaded_file.name, total)
                                        st.caption("Translation errors may occur")
                            with col2:
                                if st.button("No"):
                                    st.write("Understood")
                                        
    # Output: First half: abcd, Second half: efgh
    
                else:
                        st.text_area("Original Content Preview", file_content, height=100)
    
                        if st.button("Translate File"):
                            with st.spinner(f"Translating file to {selected_lang_name}..."):
                                translated_content = perform_translation(file_content, target_lang_code)
    
                                st.subheader("Translated Content:")
                                st.text_area("Result Preview", translated_content, height=200)
                                st.caption("Translation errors may occur")
    
                                st.download_button(
                                    label="Download Translated File",
                                    data=translated_content,
                                    file_name=f"Versatranslate_v1_{selected_lang_name}_{uploaded_file.name}",
                                    mime="text/plain"
                                )
    
    # --- HISTORY DISPLAY ---
    st.subheader("Your Translation History")
    user_id = get_current_user_id()
    history = supabase.table("translation_history").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    with st.expander("Clear translation history"):
        st.write("Are you sure, this wipes all account history?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", key="clear_history_confirm"):
                with st.spinner():
                    success, message = clear_history()
        # Render based on the result
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                            st.error(message) # Show the error nicely in the UI# Refresh only if the operation actually succeeded
        with col2:
            if st.button("No", key="n0_clear_history"):
                st.write("Understood")
                time.sleep(1)
                st.rerun()
                
                
    
    for item in history.data:
        st.markdown(f"**Lang:** `{item['target_lang']}`")
        st.write(f"📝 {item['input_text'][:100]}")
        st.markdown(f"{selected_lang_name}")
        st.write(f"Output: {item['output_text'][:100]}")
        st.divider()
except Exception as e:
    handler.log(e, code="500")
    st.write(f"{e}")
