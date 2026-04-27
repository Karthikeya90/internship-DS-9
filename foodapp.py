import streamlit as st
import sqlite3

# ---------------- DATABASE ----------------
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
conn.commit()

# ---------------- MENU DATA ----------------
menu = [
    {"name": "Pizza", "category": "Veg", "price": 200},
    {"name": "Burger", "category": "Veg", "price": 120},
    {"name": "Chicken Biryani", "category": "Non-Veg", "price": 250},
    {"name": "Pasta", "category": "Veg", "price": 150},
    {"name": "Grilled Chicken", "category": "Non-Veg", "price": 300}
]

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.title("🍔 Food App")
page = st.sidebar.radio("Go to", ["Home", "Menu", "Cart", "Orders"])

# ---------------- HOME PAGE ----------------
if page == "Home":
    st.title("🏠 Online Food Ordering System")
    st.write("Welcome to our Full Stack Food Ordering App!")
    st.info("Use the sidebar to navigate.")

# ---------------- MENU PAGE ----------------
elif page == "Menu":
    st.title("📋 Menu")

    user_name = st.text_input("Enter your name")

    category = st.selectbox("Select Category", ["All", "Veg", "Non-Veg"])

    for item in menu:
        if category == "All" or item["category"] == category:
            if st.button(f"Add {item['name']} - ₹{item['price']}"):
                if user_name.strip() == "":
                    st.warning("Enter your name first")
                else:
                    c.execute(
                        "INSERT INTO orders (name, item, category, price) VALUES (?, ?, ?, ?)",
                        (user_name, item["name"], item["category"], item["price"])
                    )
                    conn.commit()
                    st.success(f"{item['name']} added!")

# ---------------- CART PAGE ----------------
elif page == "Cart":
    st.title("🛒 Cart")

    user_name = st.text_input("Enter your name")

    if user_name.strip() != "":
        c.execute("SELECT item, category, price FROM orders WHERE name=?", (user_name,))
        orders = c.fetchall()

        total = 0

        if orders:
            for o in orders:
                st.write(f"{o[0]} ({o[1]}) - ₹{o[2]}")
                total += o[2]

            st.write(f"### 💰 Total: ₹{total}")

            if st.button("Place Order"):
                st.success("Order placed successfully!")
                c.execute("DELETE FROM orders WHERE name=?", (user_name,))
                conn.commit()
        else:
            st.info("Cart is empty")
    else:
        st.info("Enter your name to view cart")

# ---------------- ORDERS PAGE ----------------
elif page == "Orders":
    st.title("📦 Orders Info")

    st.write("This page can be used to show order history (future improvement).")

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Developed as Full Stack Web Application Demo")
