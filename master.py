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
st.title("SABPAM - Production Tracker")

with st.form("entry_form", clear_on_submit=True):
    # Form Fields as per your list
    tailor_name = st.text_input("Tailor Name")
    style_no = st.text_input("STYLE NO")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("START DATE", value=datetime.date.today())
        start_time = st.time_input("START TIME", value=datetime.time(9, 30))
    with col_d2:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        end_time = st.time_input("END TIME", value=datetime.time(18, 0))
    
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
                # --- ASLI CALCULATION (MINUTES MEIN) ---
                # Office Time Calculation: 9:30 se 18:00 = 510 minutes
                # Par hum flexible rakhte hain agar aap manual time badlo
                dt1 = datetime.datetime.combine(start_date, start_time)
                dt2 = datetime.datetime.combine(end_date, end_time)
                
                # Kul minutes (End - Start)
                gross_minutes = int((dt2 - dt1).total_seconds() / 60)
                
                # Formula: (Gross Time + Overtime) - (Hold + Loss + Alteration)
                final_minutes = (gross_minutes + overtime) - (hold_time + loss_time + alt_time)
                
                if final_minutes < 0: final_minutes = 0

                # Minutes ko HH:MM mein badalna
                h = final_minutes // 60
                m = final_minutes % 60
                final_formatted_time = f"{h}:{m:02d}"

                # Data for Sheet (Exactly as your list)
                row = [
                    tailor_name,
                    style_no,
                    str(start_date),
                    start_time.strftime("%H:%M"),
                    str(end_date),
                    end_time.strftime("%H:%M"),
                    int(hold_time),
                    int(overtime),
                    int(loss_time),
                    alt_style,
                    int(alt_time),
                    final_formatted_time  # Ye raha final sum/minus wala result
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                
                st.success(f"Data Save! Total Work Time: {final_formatted_time} ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Galti hui: {e}")
        else:
            st.warning("Bhai, Name aur Style No likhna zaroori hai!")

         

