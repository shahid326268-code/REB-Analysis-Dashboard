import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# PAGE CONFIG
st.set_page_config(page_title="JMI Engineering Dashboard", page_icon="⚡", layout="wide")

# LOGIN SYSTEM
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def login_screen():
    st.markdown("<h1 style='text-align: center; color: #008080;'>JMI Syringes & Medical Devices Ltd</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Engineering Department</h3>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "Jmi@2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# LOAD DATA - আপডেট করা অথেন্টিকেশন
@st.cache_data(ttl=60)
def load_data():
    try:
        # স্ট্রীমলিট সিক্রেট থেকে ক্রেডেনশিয়াল লোড
        creds_dict = st.secrets["GOOGLE_SHEETS"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # oauth2client এর বদলে google-auth এর Credentials ব্যবহার করা হয়েছে
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
        return pd.DataFrame(sheet.get_all_records()), client
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame(), None

# APP START
if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# (বাকি কোড আগের মতোই থাকবে...)
# [এখানে আপনার আগের কোডের বাকি অংশটুকু হুবহু বসিয়ে দিন]
