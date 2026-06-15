import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="JMI Engineering Admin", layout="wide")

# --- ১. লগইন লজিক ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def login_screen():
    st.markdown("<h1 style='text-align: center; color: #008080;'>JMI Syringes & Medical Devices Ltd</h1>", unsafe_allow_html=True)
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

# --- ২. মূল ড্যাশবোর্ড ---
if not st.session_state["password_correct"]:
    login_screen()
else:
    c1, c2 = st.columns([6, 1])
    c1.markdown("<h1 style='text-align: center;'>📊 REB Electricity Analysis</h1>", unsafe_allow_html=True)
    if c2.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

    # ডাটা লোড
    def load_data():
        try:
            creds_dict = st.secrets["GOOGLE_SHEETS"]
            scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
            client = gspread.authorize(creds)
            sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
            return pd.DataFrame(sheet.get_all_records()), client
        except:
            return pd.DataFrame(), None

    df, client = load_data()

    if not df.empty:
        # সাইডবার ফিল্টার অপশন
        st.sidebar.header("Filter Options")
        months = ["All"] + sorted(df['Month'].unique().tolist())
        selected_month = st.sidebar.selectbox("Select Month to Filter", months)

        # ফিল্টারিং লজিক
        filtered_df = df if selected_month == "All" else df[df['Month'] == selected_month]

        # টেবিল ও গ্রাফ
        st.dataframe(filtered_df, use_container_width=True)
        
        st.subheader(f"📊 Visualization for: {selected_month}")
        col1, col2 = st.columns(2)
        
        # গ্রাফের জন্য ডাটা সেটআপ
        chart_df = filtered_df.set_index('Month')
        
        with col1:
            st.write("### REB Cost vs Total Cost")
            st.bar_chart(chart_df[['REB_Cost', 'Total_Cost']])
        with col2:
            st.write("### Consumption Trends")
            st.line_chart(chart_df[['Total Unit', 'Average_Daily_Consumption']])

        # ডাটা এন্ট্রি ফর্ম
        st.sidebar.header("Add New Data")
        with st.sidebar.form("entry_form", clear_on_submit=True):
            new_month = st.selectbox("Month", ['Jan-2026', 'Feb-2026', 'Mar-2026', 'Apr-2026', 'May-2026', 'Jun-2026'])
            reb_cost = st.number_input("REB Cost", value=0.0)
            total_cost = st.number_input("Total Cost", value=0.0)
            t_unit = st.number_input("Total Unit", value=0.0)
            
            if st.form_submit_button("Save"):
                client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1.append_row([new_month, 0, 0, 0, t_unit, 0, reb_cost, total_cost, 0, 0])
                st.success("Data Saved!")
