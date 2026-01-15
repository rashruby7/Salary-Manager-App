import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Salary Manager", layout="wide")

def get_salary_cycle_start(year, month):
    cycle_date = datetime(year, month, 28)
    if cycle_date.weekday() == 5:
        cycle_date -= timedelta(days=1)
    elif cycle_date.weekday() == 6:
        cycle_date -= timedelta(days=2)
    return cycle_date.date()

def get_cycle_for_date(date):
    start = get_salary_cycle_start(date.year, date.month)
    if date < start:
        prev_month = date.month - 1 if date.month > 1 else 12
        prev_year = date.year if date.month > 1 else date.year - 1
        start = get_salary_cycle_start(prev_year, prev_month)
    end = start + timedelta(days=31)
    return start, end

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount"])

st.title("💰 Salary & Expense Manager")
salary = st.number_input("Monthly Salary", min_value=0, step=1000)

with st.form("expense_form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food","Travel","Rent","Shopping","Bills","Other"])
    amount = st.number_input("Amount", min_value=0)
    add = st.form_submit_button("Add Expense")

if add:
    st.session_state.expenses.loc[len(st.session_state.expenses)] = [date, category, amount]
    st.success("Expense added")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    today = datetime.today().date()
    start, end = get_cycle_for_date(today)

    cycle_df = df[(df["Date"].dt.date >= start) & (df["Date"].dt.date < end)]

    total = cycle_df["Amount"].sum()
    remaining = salary - total

    c1, c2, c3 = st.columns(3)
    c1.metric("Cycle Start", start)
    c2.metric("Total Expense", f"₹ {total}")
    c3.metric("Remaining Salary", f"₹ {remaining}")

    st.bar_chart(cycle_df.groupby("Category")["Amount"].sum())
    st.dataframe(df)
