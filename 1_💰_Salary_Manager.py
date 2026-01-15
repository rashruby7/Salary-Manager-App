import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Salary & Expense Manager",
    layout="wide",
)

# ------------------ UTILS ------------------
def get_salary_cycle_start(year, month):
    cycle_date = datetime(year, month, 28)

    if cycle_date.weekday() == 5:      # Saturday
        cycle_date -= timedelta(days=1)
    elif cycle_date.weekday() == 6:    # Sunday
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


# ------------------ STATE ------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount"]
    )

# ------------------ HEADER ------------------
st.markdown("## 💰 Salary & Expense Manager")
st.caption("Track expenses by salary cycle (starts on 28th or previous working day)")
st.divider()

# ------------------ SALARY CARD ------------------
salary_col, info_col = st.columns([1, 2])

with salary_col:
    st.subheader("💼 Salary")
    salary = st.number_input(
        "Monthly Salary (₹)",
        min_value=0,
        step=1000,
        help="Used to calculate remaining balance for the cycle",
    )

with info_col:
    st.info(
        "📌 **Salary Cycle Rule**\n\n"
        "- Cycle starts on **28th** of each month\n"
        "- If 28th is a weekend → previous working day\n"
        "- Expenses are grouped by this cycle"
    )

st.divider()

# ------------------ ADD EXPENSE ------------------
st.markdown("### ➕ Add Expense")

with st.container(border=True):
    with st.form("expense_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            date = st.date_input("📅 Expense Date", datetime.today())

        with c2:
            category = st.selectbox(
                "📂 Category",
                ["Food", "Travel", "Rent", "Shopping", "Bills", "Other"],
            )

        with c3:
            amount = st.number_input("💸 Amount (₹)", min_value=0)

        submitted = st.form_submit_button("Add Expense")

    if submitted:
        st.session_state.expenses.loc[len(st.session_state.expenses)] = [
            date, category, amount
        ]
        st.success("Expense added successfully")

st.divider()

# ------------------ REPORT ------------------
if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    today = datetime.today().date()
    start, end = get_cycle_for_date(today)

    cycle_df = df[
        (df["Date"].dt.date >= start)
        & (df["Date"].dt.date < end)
    ]

    total_expense = cycle_df["Amount"].sum()
    remaining = salary - total_expense

    # ---------- METRICS ----------
    st.markdown("### 📊 Current Salary Cycle Summary")

    m1, m2, m3 = st.columns(3)
    m1.metric("Cycle Start", start.strftime("%d %b %Y"))
    m2.metric("Total Expenses", f"₹ {total_expense:,.0f}")
    m3.metric(
        "Remaining Balance",
        f"₹ {remaining:,.0f}",
        delta=f"-₹ {total_expense:,.0f}",
    )

    st.divider()

    # ---------- CHART ----------
    st.markdown("### 🗂 Expense Breakdown by Category")

    if not cycle_df.empty:
        st.bar_chart(
            cycle_df.groupby("Category")["Amount"].sum(),
            use_container_width=True,
        )
    else:
        st.warning("No expenses in the current cycle yet")

    st.divider()

    # ---------- TABLE ----------
    st.markdown("### 📋 All Expenses")
    st.dataframe(
        df.sort_values("Date", ascending=False),
        use_container_width=True,
    )

else:
    st.info("No expenses added yet. Start by adding your first expense 👆")
