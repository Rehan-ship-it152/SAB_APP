import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("SAB_Production_Data").sheet1
except Exception as e:
    st.error(f"Sheet connect nahi hui: {e}")

# --- APP UI ---
st.title("SABPAM - Smart Production Tracker")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("START DATE", value=datetime.date.today())
        start_time = st.time_input("START TIME", value=datetime.datetime.now().time())
    with col_d2:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        end_time = st.time_input("END TIME", value=datetime.datetime.now().time())
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        hold_time = st.number_input("HOLD TIME (Min)", min_value=0)
        loss_time = st.number_input("LOSS TIME (Min)", min_value=0)
        overtime = st.number_input("OVERTIME (Min)", min_value=0)
    with col_e2:
        alt_style = st.text_input("ALTERATION STYLE")
        alt_time = st.number_input("ALTERATION TIME (Min)", min_value=0)

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            try:
                # --- CALCULATION AND FORMATTING ---
                dt1 = datetime.datetime.combine(start_date, start_time)
                dt2 = datetime.datetime.combine(end_date, end_time)
                
                duration = dt2 - dt1
                total_minutes = int(duration.total_seconds() / 60)
                
                if total_minutes < 0:
                    total_minutes = 0

                # Time ko sundar banane ke liye (Sirf 17:27 dikhega)
                clean_start_time = start_time.strftime("%H:%M")
                clean_end_time = end_time.strftime("%H:%M")

                row = [
                    style_no,
                    str(start_date),
                    clean_start_time, # Ab time saaf aayega
                    tailor_name,
                    str(end_date),
                    clean_end_time,   # Ab time saaf aayega
                    int(hold_time),
                    int(loss_time),
                    int(overtime),
                    alt_style,
                    int(alt_time),
                    int(total_minutes) # Ye pakka Number ban kar jayega
                ]
                
                sheet.append_row(row)
                st.success(f"Bhai, Data save ho gaya! Total Time: {total_minutes} min ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No bharo!")

