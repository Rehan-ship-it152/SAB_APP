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
st.title("SABPAM - Production Tracker")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("Tailor Name")
    style_no = st.text_input("STYLE NO")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("START DATE", value=datetime.date.today())
        # Manual time selection
        s_hour = st.number_input("Start Hour (24h format)", min_value=0, max_value=23, value=9)
        s_min = st.number_input("Start Minute", min_value=0, max_value=59, value=30)
    with col_d2:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        e_hour = st.number_input("End Hour (24h format)", min_value=0, max_value=23, value=18)
        e_min = st.number_input("End Minute", min_value=0, max_value=59, value=0)
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        hold_time = st.number_input("HOLD TIME (Min)", min_value=0)
        overtime = st.number_input("OVERTIME (Min)", min_value=0)
    with col_e2:
        loss_time = st.number_input("LOSS TIME (Min)", min_value=0)
        alt_time = st.number_input("ALTERATION TIME (Min)", min_value=0)
        
    alt_style = st.text_input("ALTERATION STYLE")

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            try:
                # --- ZERO ERROR CALCULATION ---
                # Seedha minutes mein convert kar rahe hain (No seconds involved)
                start_total_min = (s_hour * 60) + s_min
                end_total_min = (e_hour * 60) + e_min
                
                # Date ka fark agar ho
                day_diff = (end_date - start_date).days
                gross_minutes = (end_total_min - start_total_min) + (day_diff * 1440)
                
                # Formula apply karna: (Base + OT) - (Hold + Loss + Alt)
                final_minutes = (gross_minutes + overtime) - (hold_time + loss_time + alt_time)
                
                if final_minutes < 0: final_minutes = 0

                # HH:MM format taiyaar karna
                final_h = final_minutes // 60
                final_m = final_minutes % 60
                final_formatted_time = f"{final_h}:{final_m:02d}"

                # Sheet entries
                row = [
                    tailor_name,
                    style_no,
                    str(start_date),
                    f"{s_hour:02d}:{s_min:02d}",
                    str(end_date),
                    f"{e_hour:02d}:{e_min:02d}",
                    int(hold_time),
                    int(overtime),
                    int(loss_time),
                    alt_style,
                    int(alt_time),
                    final_formatted_time
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                
                st.success(f"Data Save! Total: {final_formatted_time} ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No dalo!")



