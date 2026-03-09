import streamlit as st
import pandas as pd
from datetime import datetime, time
import io

# --- Page Configuration ---
st.set_page_config(page_title="SABPAM Production System", layout="wide")
st.title("🧵 SABPAM - Tailor Production Dashboard")

# 1. Data Store (Session State)
if 'data' not in st.session_state:
    st.session_state.data = []

# 2. Entry Form (Professional Layout)
with st.form("production_form", clear_on_submit=True):
    st.subheader("📝 New Production Entry")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tailor_name = st.text_input("👤 TAILOR NAME")
        style_no = st.text_input("🔢 STYLE NO")
        overtime = st.number_input("➕ OVERTIME (Add Hours)", min_value=0.0, step=0.5)

    with col2:
        start_date = st.date_input("📅 START DATE", datetime.now())
        start_time = st.time_input("⏰ START TIME", time(9, 30))
        hold_time = st.number_input("➖ HOLD TIME (Deduct)", min_value=0.0, step=0.5)
        loss_time = st.number_input("➖ LOSS TIME (Deduct)", min_value=0.0, step=0.5)

    with col3:
        end_date = st.date_input("📅 END DATE", datetime.now())
        end_time = st.time_input("⏰ END TIME", time(18, 0))
        alt_style = st.text_input("🔧 Alteration Style")
        alt_time = st.number_input("➖ Alteration Time (Deduct)", min_value=0.0, step=0.5)

    submit = st.form_submit_button("SAVE RECORD TO EXCEL ✅")

# 3. Calculation Logic (As per your request)
if submit:
    # Basic Duty Hours (End Time - Start Time)
    dt1 = datetime.combine(start_date, start_time)
    dt2 = datetime.combine(end_date, end_time)
    duty_hrs = (dt2 - dt1).total_seconds() / 3600
    
    # --- SAHI LOGIC ---
    # Duty mein se Hold, Loss aur Alteration MINUS honge
    # Aur Overtime PLUS hoga
    total_time = (duty_hrs - hold_time - loss_time - alt_time) + overtime

    # Data Save (Proper Order for Excel)
    st.session_state.data.append({
        "TAILOR NAME": tailor_name,
        "STYLE NO": style_no,
        "START DATE": start_date.strftime('%d-%m-%Y'),
        "START TIME": start_time.strftime('%I:%M %p'),
        "END DATE": end_date.strftime('%d-%m-%Y'),
        "END TIME": end_time.strftime('%I:%M %p'),
        "HOLD TIME": hold_time,
        "LOSS TIME": loss_time,
        "OVERTIME": overtime,
        "Alteration Style": alt_style,
        "Alteration Time": alt_time,
        "TOTAL TIME": round(total_time, 2)
    })
    st.success(f"Record Saved! Total Calculated Time: {round(total_time, 2)} Hours")

# 4. Table & Excel Download
if st.session_state.data:
    st.divider()
    df = pd.DataFrame(st.session_state.data)
    
    st.subheader("📊 Current Production Table")
    st.dataframe(df, use_container_width=True)
    
    # Excel Generation
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Production_Report')
        
        # Excel formatting (Optional but makes it look good)
        workbook = writer.book
        worksheet = writer.sheets['Production_Report']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    st.download_button(
        label="📥 DOWNLOAD FINAL EXCEL REPORT",
        data=output.getvalue(),
        file_name=f"SABPAM_Report_{datetime.now().strftime('%d-%m')}.xlsx",
        mime="application/vnd.ms-excel"
    )