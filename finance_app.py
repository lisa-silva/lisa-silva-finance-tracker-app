import streamlit as st
import pandas as pd
import datetime

# --- Configuration ---
st.set_page_config(
    page_title="Where's My Money? (Transaction Tracker)",
    layout="wide"
)

# --- State Management ---
# Initialize session state for storing transactions if it doesn't exist
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=['Date', 'Type', 'Amount', 'Category', 'Description']
    )

# --- Main Application Logic ---

def finance_app():
    st.title("💰 Where's My Money? (Transaction Tracker)")
    st.markdown("A simple tool to track income and expenses and view your running balance.")

    # --- 1. Add New Transaction Section ---
    st.header("1. Add New Transaction")
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Input fields
            date = st.date_input("Date", datetime.date.today())
            transaction_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
        
        with col2:
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            
            # Dynamic category selection
            if transaction_type == "Income":
                categories = ["Salary", "Investment", "Gift", "Other Income"]
            else:
                categories = ["Groceries", "Rent", "Utilities", "Transport", "Entertainment", "Other Expense"]
            category = st.selectbox("Category", categories)
            
        with col3:
            description = st.text_input("Description (Optional)")

        submitted = st.form_submit_button("Record Transaction")

        if submitted:
            # Convert amount to negative if it's an expense
            final_amount = amount if transaction_type == "Income" else -amount
            
            # Create a new transaction row
            new_transaction = pd.DataFrame({
                'Date': [date.strftime("%Y-%m-%d")],
                'Type': [transaction_type],
                'Amount': [final_amount],
                'Category': [category],
                'Description': [description]
            })
            
            # Append the new transaction to the main DataFrame in session state
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, new_transaction], 
                ignore_index=True
            )
            st.success("Transaction recorded successfully!")

    # --- 2. Summary and Dashboard Section ---
    st.header("2. Financial Summary")

    if not st.session_state.transactions.empty:
        df = st.session_state.transactions
        
        # Calculate key metrics
        total_income = df[df['Type'] == 'Income']['Amount'].sum()
        total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
        net_balance = total_income + total_expense
        
        # Display metrics using Streamlit metrics boxes
        col_m1, col_m2, col_m3 = st.columns(3)
        
        col_m1.metric("Total Income", f"${total_income:,.2f}", "Up")
        col_m2.metric("Total Expenses", f"${abs(total_expense):,.2f}", "Down")
        col_m3.metric("Net Balance", f"${net_balance:,.2f}", 
                      "Positive" if net_balance >= 0 else "Negative")

        st.subheader("Transaction History")
        # Display the table, sorted by date
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)

        st.subheader("Expenses by Category")
        expense_df = df[df['Type'] == 'Expense']
        if not expense_df.empty:
            category_summary = expense_df.groupby('Category')['Amount'].sum().abs().sort_values(ascending=False)
            # Display a bar chart of expenses
            st.bar_chart(category_summary)
        else:
            st.info("No expenses recorded yet to show category breakdown.")
            
    else:
        st.info("No transactions recorded yet. Add one above!")

# Run the app function
finance_app()