import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# পেজ কনফিগারেশন
st.set_page_config(page_title="REB Analysis Dashboard", layout="wide")
st.title("📊 REB Electricity Unit Analysis")

# ১. ডাটা লোড করার ফাংশন
def load_data():
    try:
        # Secrets থেকে ক্রেডেনশিয়াল লোড করা
        creds_dict = st.secrets["GOOGLE_SHEETS"]
        # gspread এর জন্য উপযুক্ত ফরম্যাট
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(creds)

        # আপনার শিট আইডি
        sheet_id = '1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU'
        sheet = client.open_by_key(sheet_id).sheet1

        # সব ডাটা নিয়ে আসা
        data = sheet.get_all_records()
        return pd.DataFrame(data), client
    except Exception as e:
        st.error(f"ডাটা লোড হচ্ছে না: {e}")
        return pd.DataFrame(), None

# ডাটা লোড করা
df, client = load_data()

# ডাটা প্রদর্শন করা
if not df.empty:
    st.dataframe(df, use_container_width=True)

    # ২. সাইডবার - ডাটা এন্ট্রি ফর্ম
    st.sidebar.subheader("Add New Month Data")
    with st.sidebar.form("entry_form", clear_on_submit=True):
        new_month = st.text_input("Month (e.g., Jun-2026)")
        m5000 = st.number_input("Meter 5000", value=0.0)
        m5010 = st.number_input("Meter 5010", value=0.0)
        work_day = st.number_input("Working_Day", value=0)
        t_unit = st.number_input("Total Unit", value=0.0)
        d_cost = st.number_input("Diesel_Cost", value=0.0)
        r_cost = st.number_input("REB_Cost", value=0.0)
        t_cost = st.number_input("Total_Cost", value=0.0)

        submitted = st.form_submit_button("Save Data")
        
        # ডাটা সেভ করার লজিক
        if submitted and client:
            try:
                sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
                sheet.append_row([new_month, m5000, m5010, work_day, t_unit, d_cost, r_cost, t_cost])
                st.success("Data Saved! Please Refresh to see updates.")
            except Exception as e:
                st.error(f"ডাটা সেভ হয়নি: {e}")
else:
    st.warning("ফাইলে কোনো ডাটা পাওয়া যায়নি বা কানেকশনে সমস্যা আছে।")
