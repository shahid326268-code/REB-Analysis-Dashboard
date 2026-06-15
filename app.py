import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="JMI Engineering Dashboard",
    page_icon="⚡",
    layout="wide"
)

# =========================
# LOGIN SYSTEM (UNCHANGED)
# =========================
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

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    try:
        creds_dict = st.secrets["GOOGLE_SHEETS"]
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(creds)

        sheet = client.open_by_key(
            '1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU'
        ).sheet1

        df = pd.DataFrame(sheet.get_all_records())
        return df, client

    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame(), None


# =========================
# APP START
# =========================
if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# =========================
# HEADER
# =========================
col1, col2 = st.columns([6, 1])

col1.markdown(
    "<h1 style='text-align: center;'>📊 REB Electricity Engineering Dashboard</h1>",
    unsafe_allow_html=True
)

if col2.button("Log out"):
    st.session_state["password_correct"] = False
    st.rerun()

# =========================
# DATA
# =========================
df, client = load_data()

if df.empty:
    st.warning("No data found in Google Sheet")
    st.stop()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("🔎 Filters")

months = ["All"] + df['Month'].astype(str).unique().tolist()
selected_month = st.sidebar.selectbox("Select Month", months)

filtered_df = df.copy()
if selected_month != "All":
    filtered_df = df[df["Month"].astype(str) == selected_month]

# =========================
# SAFE NUMERIC CONVERSION
# =========================
def safe_sum(col):
    if col in filtered_df.columns:
        return pd.to_numeric(filtered_df[col], errors='coerce').fillna(0).sum()
    return 0

def safe_mean(col):
    if col in filtered_df.columns:
        return pd.to_numeric(filtered_df[col], errors='coerce').fillna(0).mean()
    return 0

# =========================
# KPI CALCULATION
# =========================
total_unit = safe_sum("Total Unit")
reb_cost = safe_sum("REB_Cost")
total_cost = safe_sum("Total_Cost")
diesel_cost = safe_sum("Diesel_Cost")
avg_daily = safe_mean("Average_Daily_Consumption")

cost_per_unit = (total_cost / total_unit) if total_unit > 0 else 0
savings = diesel_cost - reb_cost

# =========================
# KPI CARDS
# =========================
st.subheader("📌 Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric("⚡ Total Unit", f"{total_unit:,.0f}")
k2.metric("💰 REB Cost", f"৳ {reb_cost:,.0f}")
k3.metric("🏭 Total Cost", f"৳ {total_cost:,.0f}")
k4.metric("💵 Cost/Unit", f"৳ {cost_per_unit:.2f}")

k5, k6 = st.columns(2)
k5.metric("⛽ Diesel Savings", f"৳ {savings:,.0f}")
k6.metric("📊 Avg Daily Unit", f"{avg_daily:,.0f}")

# =========================
# TABLE
# =========================
st.subheader("📋 Data Table")
st.dataframe(filtered_df, use_container_width=True)

# =========================
# CHARTS
# =========================
st.subheader("📈 Analysis Dashboard")

c1, c2 = st.columns(2)

with c1:
    st.write("REB vs Total Cost")
    if "REB_Cost" in filtered_df.columns and "Total_Cost" in filtered_df.columns:
        st.bar_chart(filtered_df.set_index("Month")[["REB_Cost", "Total_Cost"]])

with c2:
    st.write("Consumption Trend")
    if "Total Unit" in filtered_df.columns:
        st.line_chart(filtered_df.set_index("Month")["Total Unit"])

# =========================
# PIE CHART
# =========================
st.subheader("🥧 Cost Distribution")

if diesel_cost or reb_cost:
    pie = pd.DataFrame({
        "Type": ["REB", "Diesel"],
        "Amount": [reb_cost, diesel_cost]
    })

    fig = px.pie(pie, names="Type", values="Amount", title="Cost Share")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# EXECUTIVE SUMMARY
# =========================
st.subheader("📝 Executive Summary")

summary = f"""
- Total Unit Consumption: {total_unit:,.0f}
- REB Cost: ৳ {reb_cost:,.0f}
- Total Cost: ৳ {total_cost:,.0f}
- Diesel Cost: ৳ {diesel_cost:,.0f}
- Cost Per Unit: ৳ {cost_per_unit:.2f}
- Estimated Savings: ৳ {savings:,.0f}
"""

st.info(summary)

# =========================
# DOWNLOAD REPORT
# =========================
csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    "📥 Download Report",
    data=csv,
    file_name="REB_Electricity_Report.csv",
    mime="text/csv"
)

# =========================
# ADD NEW DATA (SAFE)
# =========================
st.sidebar.header("➕ Add Data")

with st.sidebar.form("add_form"):
    month = st.text_input("Month")
    total_unit_in = st.number_input("Total Unit", value=0.0)
    reb_cost_in = st.number_input("REB Cost", value=0.0)
    total_cost_in = st.number_input("Total Cost", value=0.0)

    submit = st.form_submit_button("Save")

    if submit and client:
        try:
            sheet = client.open_by_key(
                '1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU'
            ).sheet1

            sheet.append_row([
                month,
                0,
                0,
                0,
                total_unit_in,
                0,
                reb_cost_in,
                total_cost_in,
                0
            ])

            st.success("Data Saved Successfully!")

        except Exception as e:
            st.error(f"Save Error: {e}")
