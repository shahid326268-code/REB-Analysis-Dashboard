import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="JMI Engineering Admin", layout="wide")

# --- ১. লগইন স্টেট চেক ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

# --- ২. লগইন ফাংশন ---
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

# --- ৩. মূল ড্যাশবোর্ড লজিক (লগইন সফল হলে এটি কাজ করবে) ---
if not st.session_state["password_correct"]:
    login_screen()
else:
    # লগআউট বাটন
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    st.title("📊 REB Electricity Unit Analysis - Dashboard")

    # ডাটা লোড করার ফাংশন
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
        # ডাটা সর্টিং এবং গ্রাফ প্রদর্শন
        month_order = ['Jan-2026', 'Feb-2026', 'Mar-2026', 'Apr-2026', 'May-2026', 'Jun-2026']
        df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
        df = df.sort_values('Month')
        df_chart = df.set_index('Month')

        st.dataframe(df, use_container_width=True)
        
        st.subheader("📊 Analytical Visualizations")
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(df_chart[['Total Unit', 'Electricity Cost per Piece (Tk/pcs)']])
        with col2:
            st.bar_chart(df_chart['Total_Cost'])
    else:
        st.warning("ডাটা খুঁজে পাওয়া যায়নি।")
