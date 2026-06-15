import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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

# LOAD DATA
@st.cache_data(ttl=60)
def load_data():
    try:
        creds_dict = st.secrets["GOOGLE_SHEETS"]
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
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

# HEADER
col1, col2 = st.columns([6, 1])
col1.markdown("<h1 style='text-align: center;'>📊 REB Electricity Engineering Dashboard</h1>", unsafe_allow_html=True)
if col2.button("Log out"):
    st.session_state["password_correct"] = False
    st.rerun()

df, client = load_data()

# SIDEBAR FILTER
st.sidebar.header("🔎 Filters")
month_order = ['Jan-2026', 'Feb-2026', 'Mar-2026', 'Apr-2026', 'May-2026', 'Jun-2026']
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
df = df.sort_values('Month')

months = ["All"] + df['Month'].astype(str).unique().tolist()
selected_month = st.sidebar.selectbox("Select Month", months)

filtered_df = df.copy()
if selected_month != "All":
    filtered_df = df[df["Month"].astype(str) == selected_month]

# KPI CALCULATIONS
total_unit = pd.to_numeric(filtered_df['Total Unit'], errors='coerce').sum()
reb_cost = pd.to_numeric(filtered_df['REB_Cost'], errors='coerce').sum()
total_cost = pd.to_numeric(filtered_df['Total_Cost'], errors='coerce').sum()
diesel_cost = pd.to_numeric(filtered_df['Diesel_Cost'], errors='coerce').sum()

# KPI METRICS
# --- KPI CALCULATION ---
total_unit = pd.to_numeric(filtered_df['Total Unit'], errors='coerce').sum()
reb_cost = pd.to_numeric(filtered_df['REB_Cost'], errors='coerce').sum()
cost_per_piece = pd.to_numeric(filtered_df['Electricity Cost per Piece (Tk/pcs)'], errors='coerce').mean() # এখানে আপনার কলামের নাম অনুযায়ী চেক করবেন

# --- KPI METRICS ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("⚡ Total Unit", f"{total_unit:,.0f}")
k2.metric("💰 REB Cost", f"৳ {reb_cost:,.0f}")
k3.metric("📈 Cost/Piece", f"৳ {cost_per_piece:.2f}") # এটি আপনার নতুন KPI

# CHARTS
st.subheader("📈 Analysis & Distribution")
c1, c2 = st.columns(2)
with c1:
    st.bar_chart(filtered_df.set_index("Month")[["REB_Cost"]])
with c2:
    pie_data = pd.DataFrame({"Type": ["REB", "Diesel"], "Amount": [reb_cost, diesel_cost]})
    fig = px.pie(pie_data, names="Type", values="Amount", title="Cost Distribution")
    st.plotly_chart(fig, use_container_width=True)

# DATA TABLE & DOWNLOAD
st.subheader("📋 Data Table")
st.dataframe(filtered_df, use_container_width=True)
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Report", data=csv, file_name="REB_Report.csv", mime="text/csv")

# SIDEBAR ADD DATA
st.sidebar.header("➕ Add New Data")
with st.sidebar.form("add_form", clear_on_submit=True):
    month = st.selectbox("Month", month_order)
    t_unit = st.number_input("Total Unit", value=0.0)
    r_cost = st.number_input("REB Cost", value=0.0)
    t_cost = st.number_input("Total Cost", value=0.0)
    if st.form_submit_button("Save Data"):
        client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1.append_row([month, 0, 0, 0, t_unit, 0, r_cost, t_cost, 0])
        st.success("Data Saved!")
