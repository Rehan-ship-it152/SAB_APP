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
st.title("SABPAM Production Tracker")

with st.form("entry_form", clear_on_submit=True):
    # Aapke bataye huye saare 10 columns yahan hain
    style_no = st.text_input("STYLE NO")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("START DATE", value=datetime.date.today())
        start_time = st.time_input("START TIME", value=datetime.time(9, 30)) # Default 9:30
    with col2:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        end_time = st.time_input("END TIME", value=datetime.time(18, 0)) # Default 18:00

    st.write("---")
    col3, col4 = st.columns(2)
    with col3:
        hold_time = st.number_input("HOLD TIME (Min)", min_value=0)
        overtime = st.number_input("OVERTIME (Min)", min_value=0)
        loss_time = st.number_input("LOSS TIME (Min)", min_value=0)
    with col4:
        alt_style = st.text_input("ALTERATION STYLE")
        alt_time = st.number_input("ALTERATION TIME (Min)", min_value=0)

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if style_no:
            try:
                # 1. Start aur End time se minutes nikalna
                dt1 = datetime.datetime.combine(start_date, start_time)
                dt2 = datetime.datetime.combine(end_date, end_time)
                
                # Kul minutes (End - Start)
                gross_minutes = int((dt2 - dt1).total_seconds() / 60)
                
                # 2. FINAL CALCULATION (SUM & MINUS)
                # Formula: (Asli Time + Overtime) - (Hold + Loss + Alteration)
                total_work_min = (gross_minutes + overtime) - (hold_time + loss_time + alt_time)
                
                if total_work_min < 0: total_work_min = 0

                # 3. Minutes ko Hours:Minutes mein badalna (e.g., 8:30)
                h = total_work_min // 60
                m = total_work_min % 60
                final_time_display = f"{h}:{m:02d}"

                # 4. Sheet mein Data bhejnat (Wahi columns jo aapne maange)
                row = [
                    tailor_name,
                    style_no,
                    str(start_date),
                    start_time.strftime("%H:%M"),
                    str(end_date),
                    end_time.strftime("%H:%M"),
                    hold_time,
                    overtime,
                    loss_time,
                    alt_style,
                    alt_time,
                    final_time_display # Final Total Calculation
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                st.success(f"Data save ho gaya! Total Calculation: {final_time_display} ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Galti hui: {e}")
        else:
            st.warning("Bhai, Style No bharo pehle!")


