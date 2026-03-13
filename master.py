import streamlit as st
import pandas as pd
import datetime
import pytz # India ka time set karne ke liye
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

# --- TIMEZONE SETUP ---
IST = pytz.timezone('Asia/Kolkata')

# --- APP UI ---
st.title("SABPAM - Smart Production Tracker (IST)")

with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("TAILOR NAME")
    style_no = st.text_input("STYLE NO")
    
    col_d1, col_d2 = st.columns(2)
    # India ke aaj ki date aur time dikhane ke liye
    now_ist = datetime.datetime.now(IST)
    
    with col_d1:
        start_date = st.date_input("START DATE", value=now_ist.date())
        start_time = st.time_input("START TIME", value=now_ist.time())
    with col_d2:
        end_date = st.date_input("END DATE", value=now_ist.date())
        end_time = st.time_input("END TIME", value=now_ist.time())
    
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
                # --- CALCULATION LOGIC ---
                # Hum input kiye gaye time ko IST mein convert kar rahe hain
                dt1 = datetime.datetime.combine(start_date, start_time)
                dt2 = datetime.datetime.combine(end_date, end_time)
                
                # Kul minutes (End - Start)
                duration = dt2 - dt1
                gross_minutes = int(duration.total_seconds() / 60)
                
                # FINAL FORMULA: (Duty Time + Overtime) - (Hold + Loss)
                # Office ka hisaab: Overtime judega, Hold aur Loss ghatega
                final_total = (gross_minutes + overtime) - (hold_time + loss_time)
                
                if final_total < 0:
                    final_total = 0

                # Formatted Time for Sheet (HH:MM)
                s_time_str = start_time.strftime("%H:%M")
                e_time_str = end_time.strftime("%H:%M")

                row = [
                    style_no,
                    str(start_date),
                    s_time_str,
                    tailor_name,
                    str(end_date),
                    e_time_str,
                    int(hold_time),
                    int(loss_time),
                    int(overtime),
                    alt_style,
                    int(alt_time),
                    int(final_total)
                ]
                
                sheet.append_row(row, value_input_option='USER_ENTERED')
                st.success(f"Bhai, Data save ho gaya! Final Total: {final_total} min ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Bhai, Name aur Style bharo!")



