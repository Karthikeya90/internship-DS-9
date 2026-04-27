import streamlit as st
import sqlite3

# Database setup
conn = sqlite3.connect('orders.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS orders
             (item TEXT, price INT)''')

# Menu
menu = {
    "Pizza": 200,
    "Burger": 120,
    "Pasta": 150,
    "Sandwich": 100
}

st.title("🍔 Online Food Ordering System")

# Show menu
st.header("Menu")
for item, price in menu.items():
    if st.button(f"Add {item} - ₹{price}"):
        c.execute("INSERT INTO orders VALUES (?, ?)", (item, price))
        conn.commit()
        st.success(f"{item} added to cart!")

# Show cart
st.header("🛒 Cart")
c.execute("SELECT * FROM orders")
orders = c.fetchall()

total = 0
for order in orders:
    st.write(order[0], "-", "₹", order[1])
    total += order[1]

st.write("### Total:", total)

# Place order
if st.button("Place Order"):
    st.success("Order Placed Successfully!")
    c.execute("DELETE FROM orders")
    conn.commit()
