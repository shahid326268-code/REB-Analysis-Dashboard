import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# পেজ কনফিগারেশন
st.set_page_config(page_title="JMI Engineering Admin", layout="centered")

# কাস্টম স্টাইল (প্রফেশনাল লুকের জন্য)
st.markdown("""
    <style>
    .main-title { text-align: center; color: #008080; font-family: sans-serif; }
    .sub-title { text-align: center; color: #555; margin-bottom: 30px; }
    .login-container { 
        padding: 40px; 
        border: 1px solid #ddd; 
        border-radius: 15px; 
        background-color: #f9f9f9; 
    }
    </style>
    """, unsafe_allow_html=True)

# লগইন ফাংশন
def check_password():
    st.markdown("<h1 class='main-title'>JMI Syringes & Medical Devices Ltd</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-title'>Engineering Department</h3>", unsafe_allow_html=True)
    
    # লগইন বক্স
    with st.container():
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        login_button = st.button("Login")
        st.markdown("</div>", unsafe_allow_html=True)

    if login_button:
        if username == "admin" and password == "Jmi@2026": # আপনার ইউজারনেম ও পাসওয়ার্ড
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")
            return False
    return st.session_state.get("password_correct", False)

# মূল অ্যাপ
if check_password():
    st.set_page_config(layout="wide") # লগইন হওয়ার পর ওয়াইড লেআউট
    st.title("📊 REB Electricity Unit Analysis - Dashboard")
    
    # [এখানে আপনার আগের ডাটা লোডিং এবং গ্রাফের কোডগুলো বসিয়ে দিন]
