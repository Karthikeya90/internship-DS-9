import streamlit as st
import sqlite3

conn = sqlite3.connect('orders.db', check_same_thread=False)
c = conn.cursor()

# FORCE RESET TABLE (fix error permanently)
c.execute("DROP TABLE IF EXISTS orders")

c.execute('''
CREATE TABLE orders (
    name TEXT,
    item TEXT,
    category TEXT,
    price INTEGER
)
''')

# Menu
menu = [
    {"name": "Pizza", "category": "Veg", "price": 200},
    {"name": "Burger", "category": "Veg", "price": 120},
    {"name": "Chicken Biryani", "category": "Non-Veg", "price": 250},
    {"name": "Pasta", "category": "Veg", "price": 150},
    {"name": "Grilled Chicken", "category": "Non-Veg", "price": 300}
]

st.title("🍔 Online Food Ordering System")

user_name = st.text_input("Enter your name")

category = st.selectbox("Category", ["All", "Veg", "Non-Veg"])

st.subheader("Menu")

for item in menu:
    if category == "All" or item["category"] == category:
        if st.button(f"Add {item['name']} - ₹{item['price']}"):
            if user_name.strip() == "":
                st.warning("Enter your name first")
            else:
                c.execute(
                    "INSERT INTO orders VALUES (?, ?, ?, ?)",
                    (user_name, item["name"], item["category"], item["price"])
                )
                conn.commit()
                st.success(f"{item['name']} added!")

# Cart
st.subheader("Cart")

if user_name.strip() != "":
    c.execute("SELECT item, category, price FROM orders WHERE name=?", (user_name,))
    orders = c.fetchall()

    total = 0

    if orders:
        for o in orders:
            st.write(f"{o[0]} ({o[1]}) - ₹{o[2]}")
            total += o[2]

        st.write("### Total:", total)

        if st.button("Place Order"):
            st.success("Order placed!")
            c.execute("DELETE FROM orders WHERE name=?", (user_name,))
            conn.commit()
    else:
        st.info("Cart empty")
else:
    st.info("Enter name to see cart")
