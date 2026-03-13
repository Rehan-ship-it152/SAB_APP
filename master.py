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

# --- 2. PREMIUM BACKGROUND & DESIGN ---
st.markdown("""
    <style>
    /* Poori screen ka background gradient */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    /* Form ko sundar box banane ke liye */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 30px !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
        border: 1px solid #e0e0e0 !important;
    }
    /* Buttons ka style */
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 10px !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DESIGNER TITLE SECTION ---
st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: white; border-radius: 15px; border-bottom: 5px solid #1E3A8A;'>
        <h1 style='color: #1E3A8A; font-family: "Georgia", serif; font-size: 40px; margin-bottom: 0;'>
            SABPAM EXPORTS
        </h1>
        <p style='color: #8B4513; font-size: 18px; font-weight: bold; letter-spacing: 5px; text-transform: uppercase; margin-top: 5px;'>
            High Fashion Company
        </p>
    </div>
    <br>
    """, unsafe_allow_html=True)

# --- 4. PRODUCTION FORM ---
with st.form("production_main_form", clear_on_submit=True):
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
    st.write("**Productivity Details (Hours mein dalo, jaise 1.5)**")
    
    col_c, col_d = st.columns(2)
    with col_c:
        hold_h = st.number_input("HOLD (Hours)", min_value=0.0, step=0.1)
        ot_h = st.number_input("OVERTIME (Hours)", min_value=0.0, step=0.1)
    
    with col_d:
        loss_h = st.number_input("LOSS (Hours)", min_value=0.0, step=0.1)
        alt_h = st.number_input("ALTERATION (Hours)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("SUBMIT PRODUCTION DATA")

    if submitted:
        if tailor_name and style_no:
            # 1. Calculation Logic
            s_min = start_time.hour * 60 + start_time.minute
            e_min = end_time.hour * 60 + end_time.minute
            day_diff = (end_date - start_date).days
            gross_min = (e_min - s_min) + (day_diff * 1440)
            
            # 2. Minutes conversion
            ot_min = ot_h * 60
            hold_min = hold_h * 60
            loss_min = loss_h * 60
            alt_min = alt_h * 60
            
            # 3. Final total calculation
            total_min = (gross_min + ot_min) - (hold_min + loss_min + alt_min)
            
            if total_min < 0: total_min = 0
            
            # 4. HH:MM Format
            h = int(total_min // 60)
            m = int(total_min % 60)
            final_time = f"{h}:{m:02d}"

            # 5. Row data for Sheets
            row = [
                tailor_name, style_no, str(start_date), start_time.strftime("%H:%M"),
                str(end_date), end_time.strftime("%H:%M"), hold_h, ot_h, loss_h, 
                alt_style, alt_h, final_time
            ]
            
            try:
                sheet.append_row(row, value_input_option='USER_ENTERED')
                st.success(f"Data Saved Successfully! Total Production Time: {final_time} ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Saving error: {e}")
        else:
            st.warning("Bhai, Tailor Name aur Style No bhul gaye aap!")











