import streamlit as st
import sqlite3

# Database
conn = sqlite3.connect('orders.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    name TEXT,
    item TEXT,
    category TEXT,
    price INTEGER
)
''')

# Sidebar navigation
page = st.sidebar.selectbox("Select Page", ["🍔 Order Food", "📍 Delivery Details"])

# Menu data
menu = [
    {"name": "Pizza", "category": "Veg", "price": 200},
    {"name": "Burger", "category": "Veg", "price": 120},
    {"name": "Chicken Biryani", "category": "Non-Veg", "price": 250},
    {"name": "Pasta", "category": "Veg", "price": 150},
    {"name": "Grilled Chicken", "category": "Non-Veg", "price": 300}
]

# ---------------- PAGE 1 ----------------
if page == "🍔 Order Food":
    st.title("🍔 Online Food Ordering System")

    user_name = st.text_input("Enter your name")

    category_filter = st.selectbox("Select Category", ["All", "Veg", "Non-Veg"])

    st.subheader("📋 Menu")

    for item in menu:
        if category_filter == "All" or item["category"] == category_filter:
            if st.button(f"Add {item['name']} - ₹{item['price']}"):
                if user_name.strip() == "":
                    st.warning("Please enter your name first")
                else:
                    c.execute(
                        "INSERT INTO orders (name, item, category, price) VALUES (?, ?, ?, ?)",
                        (user_name, item["name"], item["category"], item["price"])
                    )
                    conn.commit()
                    st.success(f"{item['name']} added!")

    # Cart
    st.subheader("🛒 Cart")

    if user_name.strip() != "":
        c.execute("SELECT item, category, price FROM orders WHERE name=?", (user_name,))
        orders = c.fetchall()

        total = 0

        if orders:
            for order in orders:
                st.write(f"{order[0]} ({order[1]}) - ₹{order[2]}")
                total += order[2]

            st.write(f"### 💰 Total: ₹{total}")

            if st.button("Proceed to Delivery"):
                st.success("Go to Delivery Details page ➡️")
        else:
            st.info("Cart is empty")
    else:
        st.info("Enter name to view cart")

# ---------------- PAGE 2 ----------------
elif page == "📍 Delivery Details":
    st.title("📍 Delivery Information")

    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Delivery Address")
    city = st.text_input("City")

    if st.button("Confirm Order"):
        if name and phone and address and city:
            st.success("✅ Order Confirmed!")
            st.write("🚚 Your food will be delivered soon")
        else:
            st.warning("Please fill all details")

# Footer
st.markdown("---")
st.write("Full Stack Food Ordering Demo Project")
