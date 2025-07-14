import streamlit as st
import pandas as pd
import sqlite3

st.title("Invoice Analytics Dashboard")

# Connect to SQLite DB
def get_data():
    conn = sqlite3.connect("invoices.db")
    df = pd.read_sql_query("SELECT * FROM invoices", conn)
    conn.close()
    return df

df = get_data()

if df.empty:
    st.info("No invoices found. Upload some invoices first!")
else:
    st.subheader("All Invoices")
    st.dataframe(df)

    st.subheader("Total Expenses")
    st.metric("Total Amount", f"${df['amount'].sum():,.2f}")

    st.subheader("Expenses by Category")
    cat = df.groupby('category')['amount'].sum().reset_index()
    st.bar_chart(cat, x='category', y='amount')

    st.subheader("Expenses by Vendor")
    vend = df.groupby('vendor')['amount'].sum().reset_index()
    st.bar_chart(vend, x='vendor', y='amount')

    st.subheader("Expenses Over Time")
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        time = df.groupby('date')['amount'].sum().reset_index()
        st.line_chart(time, x='date', y='amount') 