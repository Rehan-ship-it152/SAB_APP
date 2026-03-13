
import streamlit as st
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("SAB_Production_Data").sheet1
except Exception as e:
    st.error(f"Sheet error: {e}")

# --- 2. OLD CLEAN DESIGN (Wahi pehle wala) ---
st.markdown("""
    <div style='text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-bottom: 5px solid #1E3A8A;'>
        <h1 style='color: #1E3A8A; font-family: "Arial Black", Gadget, sans-serif; margin-bottom: 0;'>
            SABPAM EXPORTS
        </h1>
        <p style='color: #555; font-size: 18px; font-weight: bold; letter-spacing: 2px;'>
            HIGH FASHION COMPANY
        </p>
    </div>
    <br>
    """, unsafe_allow_html=True)

# --- 3. THE FORM (Sirf Ek Baar) ---
with st.form("main_production_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        tailor_name = st.text_input("Tailor Name")
        style_no = st.text_input("STYLE NO")
        start_date = st.date_input("START DATE", value=datetime.date.today())
        start_time = st.time_input("START TIME", value=datetime.time(9, 30))
    
    with col_b:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        end_time = st.time_input("END TIME", value=datetime.time(18, 0))
        alt_style = st.text_input("ALTERATION STYLE")

    st.write("---")
    st.write("**Productivity Details (Hours mein data dalo)**")
    
    col_c, col_d = st.columns(2)
    with col_c:
        hold_h = st.number_input("HOLD (Hours)", min_value=0.0, step=0.1)
        ot_h = st.number_input("OVERTIME (Hours)", min_value=0.0, step=0.1)
    with col_d:
        loss_h = st.number_input("LOSS (Hours)", min_value=0.0, step=0.1)
        alt_h = st.number_input("ALTERATION (Hours)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            # Calculation logic
            s_min = start_time.hour * 60 + start_time.minute
            e_min = end_time.hour * 60 + end_time.minute
            day_diff = (end_date - start_date).days
            gross_min = (e_min - s_min) + (day_diff * 1440)
            
            total_min = (gross_min + (ot_h * 60)) - ((hold_h * 60) + (loss_h * 60) + (alt_h * 60))
            if total_min < 0: total_min = 0

            h, m = int(total_min // 60), int(total_min % 60)
            final_time = f"{h}:{m:02d}"

            row = [tailor_name, style_no, str(start_date), start_time.strftime("%H:%M"),
                   str(end_date), end_time.strftime("%H:%M"), hold_h, ot_h, loss_h, 
                   alt_style, alt_h, final_time]
            
            sheet.append_row(row, value_input_option='USER_ENTERED')
            st.success(f"Data Saved! Total: {final_time} ✅")
            st.balloons()










