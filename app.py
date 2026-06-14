import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="JMI Engineering Admin", layout="wide")

# লগইন লজিক
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def login():
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

# যদি লগইন সফল না হয়, তবে লগইন পেজ দেখাও
if not st.session_state["password_correct"]:
    login()
else:
    # লগইন সফল হলে এখানে আপনার মূল ড্যাশবোর্ডের কোড থাকবে
    st.title("📊 REB Electricity Unit Analysis - Dashboard")
    # ... এখানে ডাটা লোডিং ও গ্রাফের বাকি কোড বসান ...
    
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
