import streamlit as st
import sqlite3

# Database setup
conn = sqlite3.connect('orders.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS orders
             (name TEXT, item TEXT, category TEXT, price INT)''')

# Menu data
menu = [
    {"name": "Pizza", "category": "Veg", "price": 200},
    {"name": "Burger", "category": "Veg", "price": 120},
    {"name": "Chicken Biryani", "category": "Non-Veg", "price": 250},
    {"name": "Pasta", "category": "Veg", "price": 150},
    {"name": "Grilled Chicken", "category": "Non-Veg", "price": 300}
]

st.title("🍔 Online Food Ordering System")

# User input
user_name = st.text_input("Enter your name")

# Category filter
category_filter = st.selectbox("Select Category", ["All", "Veg", "Non-Veg"])

st.subheader("📋 Menu")

# Display menu
for item in menu:
    if category_filter == "All" or item["category"] == category_filter:
        if st.button(f"Add {item['name']} - ₹{item['price']}"):
            c.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", 
                      (user_name, item["name"], item["category"], item["price"]))
            conn.commit()
            st.success(f"{item['name']} added to cart!")

# Show cart
st.subheader("🛒 Cart")

c.execute("SELECT * FROM orders WHERE name=?", (user_name,))
orders = c.fetchall()

total = 0

if orders:
    for order in orders:
        st.write(f"{order[1]} ({order[2]}) - ₹{order[3]}")
        total += order[3]

    st.write("### 💰 Total Amount:", total)

    # Place order
    if st.button("Place Order"):
        st.success(f"Order placed successfully! Thank you {user_name}")
        c.execute("DELETE FROM orders WHERE name=?", (user_name,))
        conn.commit()
else:
    st.info("Cart is empty")

# Footer
st.markdown("---")
st.write("Developed as a Full Stack Demo Project")
