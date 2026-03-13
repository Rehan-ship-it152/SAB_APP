
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
st.title("SABPAM - Final Production Tracker")
st.subheader("Office Duty: 8 Hours 30 Minutes")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    st.write("---")
    st.write("Input (Minutes mein dalo, code ghante bana dega):")
    col1, col2 = st.columns(2)
    with col1:
        ot_min = st.number_input("OVERTIME (Min)", min_value=0)
        hold_min = st.number_input("HOLD TIME (Min)", min_value=0)
    with col2:
        loss_min = st.number_input("LOSS TIME (Min)", min_value=0)
        alt_time_min = st.number_input("ALTERATION TIME (Min)", min_value=0)

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            try:
                # 1. Base Office Time (8:30 = 510 Minutes)
                base_minutes = 510 
                
                # 2. Final Minutes Calculation
                # (8:30 + Overtime) - (Hold + Loss + Alteration)
                total_min = (base_minutes + ot_min) - (hold_min + loss_min + alt_time_min)
                
                if total_min < 0: total_min = 0

                # 3. Minutes ko HH:MM Format mein badalna
                hours = total_min // 60
                minutes = total_min % 60
                final_output = f"{hours}:{minutes:02d}"

                # 4. Sheet Data
                row = [
                    style_no,
                    datetime.date.today().strftime("%Y-%m-%d"),
                    tailor_name,
                    hold_min,
                    loss_min,
                    ot_min,
                    alt_time_min,
                    final_output # Sheet mein "8:30" dikhega
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                
                st.success(f"Data Save! Total Work Done: {final_output} (Hours:Minutes) ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Galti hui: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No bharo!")

