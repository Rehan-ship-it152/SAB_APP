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
    st.error(f"Sheet connect nahi hui. Error: {e}")

# --- APP UI ---
st.title("SABPAM - Production in Hours")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("START DATE")
        start_time = st.time_input("START TIME")
    with col_d2:
        end_date = st.date_input("END DATE")
        end_time = st.time_input("END TIME")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        # Ab aap minutes hi dalo, code khud ghante bana dega
        hold_min = st.number_input("HOLD TIME (Minutes)", min_value=0)
        loss_min = st.number_input("LOSS TIME (Minutes)", min_value=0)
        ot_min = st.number_input("OVERTIME (Minutes)", min_value=0)
    with col_e2:
        alt_style = st.text_input("ALTERATION STYLE")
        alt_time = st.number_input("ALTERATION TIME (Minutes)", min_value=0)

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            try:
                # 1. Ghante aur Minutes ka difference nikalna
                s_min = start_time.hour * 60 + start_time.minute
                e_min = end_time.hour * 60 + end_time.minute
                date_diff = (end_date - start_date).days
                total_diff_min = (e_min - s_min) + (date_diff * 1440)
                
                # 2. Saare inputs ko Hours mein badalna
                duty_hours = total_diff_min / 60
                ot_hours = ot_min / 60
                hold_hours = hold_min / 60
                loss_hours = loss_min / 60
                
                # 3. FINAL CALCULATION (In Hours)
                # Formula: (Duty + Overtime) - (Hold + Loss)
                final_total_hours = round((duty_hours + ot_hours) - (hold_hours + loss_hours), 2)
                
                if final_total_hours < 0: final_total_hours = 0

                row = [
                    style_no, str(start_date), start_time.strftime("%H:%M"), 
                    tailor_name, str(end_date), end_time.strftime("%H:%M"),
                    hold_min, loss_min, ot_min, alt_style, alt_time, 
                    final_total_hours # Ye Ghante (Hours) mein jayega (e.g. 8.5)
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                st.success(f"Bhai, Data save ho gaya! Total Time: {final_total_hours} Hours ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")



