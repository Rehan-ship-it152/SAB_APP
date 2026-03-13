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
st.title("SABPAM - Final Production Tracker")

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
                # --- SIMPLE CALCULATION (No Timezone Jhanjhat) ---
                # Hum manually ghante aur minute nikal rahe hain
                start_minutes = start_time.hour * 60 + start_time.minute
                end_minutes = end_time.hour * 60 + end_time.minute
                
                # Agar kaam agle din khatam hua toh (Date difference)
                date_diff = (end_date - start_date).days
                total_diff_minutes = (end_minutes - start_minutes) + (date_diff * 1440)
                
                # FINAL FORMULA: (Duty + Overtime) - (Hold + Loss)
                final_total = (total_diff_minutes + overtime) - (hold_time + loss_time)
                
                if final_total < 0: final_total = 0

                # Formatted Time (Jo dikh raha hai wahi jayega)
                s_t = start_time.strftime("%H:%M")
                e_t = end_time.strftime("%H:%M")

                row = [
                    style_no, str(start_date), s_t, tailor_name,
                    str(end_date), e_t, int(hold_time), int(loss_time),
                    int(overtime), alt_style, int(alt_time), int(final_total)
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                st.success(f"Bhai, Data save ho gaya! Total: {final_total} min ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Bhai, Name aur Style bharo!")


