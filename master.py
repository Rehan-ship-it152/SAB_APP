import streamlit as st
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
    st.error(f"Sheet error: {e}")
    # --- 1. BACKGROUND & STYLE (Ye sabse pehle aayega) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 30px !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
        border: 1px solid #e0e0e0 !important;
    }
    h1 {
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGO SECTION ---
# Agar logo hai toh link dalo, nahi toh ye line placeholder dikhayegi
st.image("https://via.placeholder.com/800x150.png?text=SABPAM+EXPORTS+LOGO", use_container_width=True)

# --- 3. DESIGNER TITLE SECTION ---
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #1E3A8A; font-family: "Georgia", serif; font-size: 50px; margin-bottom: 0;'>
            SABPAM EXPORTS
        </h1>
        <p style='color: #8B4513; font-size: 22px; font-weight: bold; letter-spacing: 6px; text-transform: uppercase; margin-top: 0;'>
            High Fashion Company
        </p>
        <div style='width: 150px; height: 4px; background: #1E3A8A; margin: 10px auto;'></div>
    </div>
    <br>
    """, unsafe_allow_html=True)

# --- LOGO SECTION ---
# Agar aapke paas logo ka link hai toh niche "LINK_YAHAN_DALO" ki jagah daal dein
# Agar nahi hai, toh is line ke shuru mein # laga kar ise band kar dein
st.image("https://via.placeholder.com/800x150.png?text=SABPAM+EXPORTS+LOGO", use_container_width=True)

# --- DESIGNER TITLE SECTION ---
st.markdown("""
    <div style='text-align: center; background-color: #ffffff; padding: 10px; border-radius: 5px;'>
        <h1 style='color: #1E3A8A; font-family: "Times New Roman", Times, serif; font-size: 45px; margin-bottom: 0; letter-spacing: 2px;'>
            SABPAM EXPORTS
        </h1>
        <p style='color: #8B4513; font-size: 20px; font-weight: bold; font-family: sans-serif; letter-spacing: 5px; margin-top: 0;'>
            HIGH FASHION COMPANY
        </p>
        <hr style='border: 1px solid #1E3A8A; width: 50%; margin: auto;'>
    </div>
    <br>
    """, unsafe_allow_html=True)
with st.form("entry_form", clear_on_submit=True):
    tailor_name = st.text_input("Tailor Name")
    style_no = st.text_input("STYLE NO")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("START DATE", value=datetime.date.today())
        start_time = st.time_input("START TIME", value=datetime.time(9, 30))
    with col2:
        end_date = st.date_input("END DATE", value=datetime.date.today())
        end_time = st.time_input("END TIME", value=datetime.time(18, 0))
    
    st.write("---")
    st.write("**Ghante (Hours) mein data dalo (e.g., 1.5 matlab 1 ghanta 30 min)**")
    c1, c2 = st.columns(2)
    with c1:
        hold_h = st.number_input("HOLD (Hours)", min_value=0.0, step=0.1)
        ot_h = st.number_input("OVERTIME (Hours)", min_value=0.0, step=0.1)
    with c2:
        loss_h = st.number_input("LOSS (Hours)", min_value=0.0, step=0.1)
        alt_h = st.number_input("ALTERATION (Hours)", min_value=0.0, step=0.1)
    
    alt_style = st.text_input("ALTERATION STYLE")
    submitted = st.form_submit_button("SUBMIT DATA")

    if submitted:
        if tailor_name and style_no:
            # 1. Start aur End ke beech ke minutes
            s_min = start_time.hour * 60 + start_time.minute
            e_min = end_time.hour * 60 + end_time.minute
            day_diff = (end_date - start_date).days
            gross_min = (e_min - s_min) + (day_diff * 1440)
            
            # 2. Jo ghante aapne dale unhe minutes mein badalna
            ot_min = ot_h * 60
            hold_min = hold_h * 60
            loss_min = loss_h * 60
            alt_min = alt_h * 60
            
            # 3. Final Calculation
            total_min = (gross_min + ot_min) - (hold_min + loss_min + alt_min)
            
            # 4. Result ko wapas HH:MM format mein badalna
            h = int(total_min // 60)
            m = int(total_min % 60)
            final_time = f"{h}:{m:02d}"

            row = [tailor_name, style_no, str(start_date), start_time.strftime("%H:%M"),
                   str(end_date), end_time.strftime("%H:%M"), hold_h, ot_h, loss_h, 
                   alt_style, alt_h, final_time]
            
            sheet.append_row(row, value_input_option='USER_ENTERED')
            st.success(f"Done! Total: {final_time}")
            st.balloons()






