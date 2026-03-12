import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- GOOGLE SHEETS SETUP ---
# Ye hissa Google Sheet se baat karne ke liye hai
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Streamlit Secrets se chabi (Credentials) uthana
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Sheet kholna (Dhyan rahe Sheet ka naam exact yahi ho)
    sheet = client.open("SAB_Production_Data").sheet1
except Exception as e:
    st.error(f"Google Sheet connect nahi hui. Check karo ki Sheet ka naam 'SAB_Production_Data' hai ya nahi. Error: {e}")

# --- APP KI SHAKAL (UI) ---
st.title("SABPAM - Production Entry")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("START TIME", value=datetime.now().time())
    with col2:
        end_time = st.time_input("END TIME", value=datetime.now().time())
    
    hold_time = st.number_input("HOLD TIME (Minutes)", min_value=0)
    loss_time = st.number_input("LOSS TIME (Minutes)", min_value=0)
    
    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            try:
                # Data ki ek line taiyaar karna
                row = [
                    current_date, 
                    tailor_name, 
                    style_no, 
                    str(start_time), 
                    str(end_time), 
                    hold_time, 
                    loss_time
                ]
                # Google Sheet mein aakhri row ke niche naya data jodna
                sheet.append_row(row)
                st.success("Bhai, data Google Sheet mein pahonch gaya! ✅")
                st.balloons() # Thodi khushi manane ke liye balloons
            except Exception as e:
                st.error(f"Data bhejne mein galti hui: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No likhna zaroori hai!")
