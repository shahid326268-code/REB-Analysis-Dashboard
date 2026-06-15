import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="JMI Engineering Admin", layout="wide")

# --- ১. লগইন লজিক ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def login_screen():
    st.markdown("<h1 style='text-align: center;'>JMI Syringes & Medical Devices Ltd</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Engineering Department</h3>", unsafe_allow_html=True)
    
    with st.container():
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "Jmi@2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")

# --- ২. মূল অ্যাপ (লগইন সফল হলে চলবে) ---
if not st.session_state["password_correct"]:
    login_screen()
else:
    # লগআউট বাটন
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    st.title("📊 REB Electricity Unit Analysis - Dashboard")

    # ডাটা লোড ফাংশন
    def load_data():
        try:
            creds_dict = st.secrets["GOOGLE_SHEETS"]
            scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
            client = gspread.authorize(creds)
            sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
            return pd.DataFrame(sheet.get_all_records()), client
        except Exception as e:
            st.error(f"ডাটা লোড হচ্ছে না: {e}")
            return pd.DataFrame(), None

    df, client = load_data()

    if not df.empty:
        # ডাটা টেবিল ও গ্রাফ
        st.dataframe(df, use_container_width=True)
        
        st.subheader("📊 Analytical Visualizations")
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(df[['Total Unit']])
        with col2:
            st.bar_chart(df[['Total_Cost']])

        # --- সাইডবার ডাটা এন্ট্রি ফর্ম ---
        st.sidebar.subheader("Add New Month Data")
        with st.sidebar.form("entry_form", clear_on_submit=True):
            new_month = st.text_input("Month")
            m5000 = st.number_input("Meter 5000", value=0.0)
            m5010 = st.number_input("Meter 5010", value=0.0)
            work_day = st.number_input("Working_Day", value=0)
            t_unit = st.number_input("Total Unit", value=0.0)
            d_cost = st.number_input("Diesel_Cost", value=0.0)
            r_cost = st.number_input("REB_Cost", value=0.0)
            t_cost = st.number_input("Total_Cost", value=0.0)
            cp = st.number_input("Cost per Piece", value=0.0)

            submitted = st.form_submit_button("Save Data")
            if submitted and client:
                sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
                sheet.append_row([new_month, m5000, m5010, work_day, t_unit, d_cost, r_cost, t_cost, cp])
                st.success("Data Saved!")
