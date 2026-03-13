import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Streamlit Secrets se credentials uthana
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Sheet ka naam check kar lena: SAB_Production_Data
    sheet = client.open("SAB_Production_Data").sheet1
except Exception as e:
    st.error(f"Sheet connect nahi hui. Check karo Credentials aur Sheet Name. Error: {e}")

# --- APP UI ---
st.title("SABPAM - Live Production Tracker")

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
                # --- AUTO CALCULATION LOGIC ---
                # 1. Start aur End ko combine karke full time nikalna
                dt1 = datetime.datetime.combine(start_date, start_time)
                dt2 = datetime.datetime.combine(end_date, end_time)
                
                # 2. Kul minutes nikalna (End - Start)
                duration = dt2 - dt1
                gross_minutes = int(duration.total_seconds() / 60)
                
                # 3. FINAL TOTAL FORMULA (SUM & MINUS)
                # Kaam ka waqt + Overtime - (Rukawat ka waqt)
                final_total = (gross_minutes + overtime) - (hold_time + loss_time)
                
                if final_total < 0:
                    final_total = 0

                # Time format ko saaf karna (17:27)
                clean_start_time = start_time.strftime("%H:%M")
                clean_end_time = end_time.strftime("%H:%M")

                # Row taiyaar karna
                row = [
                    style_no,
                    str(start_date),
                    clean_start_time,
                    tailor_name,
                    str(end_date),
                    clean_end_time,
                    int(hold_time),
                    int(loss_time),
                    int(overtime),
                    alt_style,
                    int(alt_time),
                    int(final_total) # Ye column apne aap calculate hokar jayega
                ]
                
                # Sheet mein data bhejnat
                # 'USER_ENTERED' zaroori hai taaki calculation/formula sahi chale
                sheet.append_row(row, value_input_option='USER_ENTERED')
                
                st.success(f"Bhai, Data save ho gaya! Total Time: {final_total} minutes ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Data bhejne mein galti hui: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No likhna zaroori hai!")



