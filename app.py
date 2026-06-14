import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# পেজ কনফিগারেশন
st.set_page_config(page_title="REB Analysis Dashboard", layout="wide")
st.subheader("JMI Syringes & Medical Devices Ltd")
st.title("📊 REB Electricity Unit Analysis")

# ১. ডাটা লোড করার ফাংশন
def load_data():
    try:
        creds_dict = st.secrets["GOOGLE_SHEETS"]
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(creds)
        sheet_id = '1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU'
        sheet = client.open_by_key(sheet_id).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data), client
    except Exception as e:
        st.error(f"ডাটা লোড হচ্ছে না: {e}")
        return pd.DataFrame(), None

# ডাটা লোড করা
df, client = load_data()

if not df.empty:
    # মাসের ক্রমানুসারে সাজানো
    month_order = ['Jan-2026', 'Feb-2026', 'Mar-2026', 'Apr-2026', 'May-2026', 'Jun-2026']
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
    df = df.sort_values('Month')
    
    # ইনডেক্স সেট করা গ্রাফের জন্য
    df_chart = df.set_index('Month')

    # ডাটা টেবিল প্রদর্শন
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Analytical Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Monthly Total Unit Consumption")
        st.line_chart(df_chart['Total Unit'])
        
        st.write("### Electricity Cost per Piece")
        st.line_chart(df_chart['Electricity Cost per Piece (Tk/pcs)'])
        
    with col2:
        st.write("### Monthly Total Cost Analysis")
        st.bar_chart(df_chart['Total_Cost'])

    # এভারেজ মাসিক ইউনিটের জন্য ম্যাট্রিক কার্ড
    st.markdown("---")
    avg_unit = df['Total Unit'].mean()
    avg_cost = df['Total_Cost'].mean()
    
    m1, m2 = st.columns(2)
    m1.metric("Average Monthly Unit", f"{avg_unit:,.2f}")
    m2.metric("Average Monthly Cost", f"{avg_cost:,.2f} BDT")

    # সাইডবার - ডাটা এন্ট্রি ফর্ম
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
        cost_p = st.number_input("Cost per Piece", value=0.0)

        submitted = st.form_submit_button("Save Data")
        
        if submitted and client:
            try:
                sheet = client.open_by_key('1OOSHOOZWE_1n2GVDbym0P70GNYx0hK26da6oQRh6PbU').sheet1
                # নতুন কলাম (cost_p) যোগ করা হয়েছে
                sheet.append_row([new_month, m5000, m5010, work_day, t_unit, d_cost, r_cost, t_cost, cost_p])
                st.success("Data Saved! Please Refresh.")
            except Exception as e:
                st.error(f"ডাটা সেভ হয়নি: {e}")
else:
    st.warning("ফাইলে কোনো ডাটা পাওয়া যায়নি।")
