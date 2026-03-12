import streamlit as st
import pandas as pd
from datetime import datetime
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
st.title("SABPAM - Full Production Entry")

with st.form("entry_form", clear_on_submit=True):
    # Row 1: Tailor aur Style
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    # Row 2: Dates
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("START DATE", value=datetime.now())
    with col_d2:
        end_date = st.date_input("END DATE", value=datetime.now())

    # Row 3: Times
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_time = st.time_input("START TIME", value=datetime.now().time())
    with col_t2:
        end_time = st.time_input("END TIME", value=datetime.now().time())
    
    # Row 4: Extra Times
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        hold_time = st.number_input("HOLD TIME (Min)", min_value=0)
        loss_time = st.number_input("LOSS TIME (Min)", min_value=0)
        overtime = st.number_input("OVERTIME (Min)", min_value=0)
    with col_e2:
        alt_style = st.text_input("ALTERATION STYLE")
        alt_time = st.number_input("ALTERATION TIME (Min)", min_value=0)
        total_time = st.number_input("TOTAL TIME (Min)", min_value=0)
    
    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            try:
                # Aapke columns ke order mein data
                row = [
                    style_no,
                    str(start_date),
                    str(start_time),
                    tailor_name,
                    str(end_date),
                    str(end_time),
                    hold_time,
                    loss_time,
                    overtime,
                    alt_style,
                    alt_time,
                    total_time
                ]
                sheet.append_row(row)
                st.success("Bhai, saara data save ho gaya! ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Data bhejne mein galti hui: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No toh likho!")
