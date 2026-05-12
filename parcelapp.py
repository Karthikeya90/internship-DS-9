# smart_logistics_app.py
# FULL STREAMLIT + MYSQL PROJECT
# Smart Logistics & Delivery Management Application

# ---------------- INSTALLATION ----------------
# pip install streamlit mysql-connector-python pandas

# ---------------- IMPORTS ----------------
import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Logistics App",
    page_icon="🚚",
    layout="wide"
)

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="smart_logistics"
)

cursor = db.cursor()

# ---------------- DATABASE TABLES ----------------

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    role VARCHAR(50)
)
""")

# ORDERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    pickup_location VARCHAR(255),
    drop_location VARCHAR(255),
    package_type VARCHAR(100),
    status VARCHAR(100),
    assigned_driver VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# REVIEWS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews(
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    rating INT,
    review TEXT
)
""")

db.commit()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "Splash"

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- FUNCTIONS ----------------

# SPLASH SCREEN
def splash_screen():

    st.title("🚚 Smart Logistics & Delivery Management App")

    st.image(
        "https://cdn-icons-png.flaticon.com/512/2972/2972185.png",
        width=180
    )

    st.subheader("Fast • Smart • Reliable Delivery Service")

    st.write("""
    ✔ Real-Time Package Tracking  
    ✔ Driver Management  
    ✔ Delivery Notifications  
    ✔ Analytics Dashboard  
    """)

    if st.button("Enter Application"):
        st.session_state.page = "Onboarding"


# ONBOARDING SCREEN
def onboarding_screen():

    st.title("✨ Welcome")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📦 Easy Delivery Booking")

    with col2:
        st.success("🗺 Live Package Tracking")

    with col3:
        st.warning("🚗 Smart Driver Management")

    st.markdown("---")

    st.subheader("Choose Login Type")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("👤 User Login"):
            st.session_state.role = "User"
            st.session_state.page = "Login"

    with c2:
        if st.button("🚗 Driver Login"):
            st.session_state.role = "Driver"
            st.session_state.page = "Login"

    with c3:
        if st.button("🏢 Admin Login"):
            st.session_state.role = "Admin"
            st.session_state.page = "Login"


# LOGIN SCREEN
def login_screen():

    st.title(f"{st.session_state.role} Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        # ADMIN LOGIN
        if st.session_state.role == "Admin":

            if username == "admin" and password == "admin123":

                st.success("Admin Login Successful")

                st.session_state.username = username
                st.session_state.page = "Admin Dashboard"

            else:
                st.error("Invalid Admin Credentials")

        else:

            query = """
            SELECT * FROM users
            WHERE username=%s AND password=%s AND role=%s
            """

            cursor.execute(
                query,
                (username, password, st.session_state.role)
            )

            result = cursor.fetchone()

            if result:

                st.success("Login Successful")

                st.session_state.username = username

                if st.session_state.role == "User":
                    st.session_state.page = "Home"

                elif st.session_state.role == "Driver":
                    st.session_state.page = "Driver Dashboard"

            else:
                st.error("Invalid Credentials")

    st.markdown("---")

    st.subheader("New User Registration")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Register"):

        insert_query = """
        INSERT INTO users(username,password,role)
        VALUES(%s,%s,%s)
        """

        cursor.execute(
            insert_query,
            (new_user, new_pass, st.session_state.role)
        )

        db.commit()

        st.success("Registration Successful")


# USER HOME SCREEN
def home_screen():

    st.title("🏠 User Home")

    st.subheader("Place Delivery Request")

    pickup = st.text_input("Pickup Location")

    drop = st.text_input("Drop Location")

    package = st.selectbox(
        "Package Type",
        [
            "Documents",
            "Food",
            "Electronics",
            "Clothes",
            "Other"
        ]
    )

    if st.button("Place Order"):

        query = """
        INSERT INTO orders(
            customer_name,
            pickup_location,
            drop_location,
            package_type,
            status,
            assigned_driver
        )
        VALUES(%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                st.session_state.username,
                pickup,
                drop,
                package,
                "Pending",
                "Not Assigned"
            )
        )

        db.commit()

        st.success("Delivery Request Placed Successfully")

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📍 Track Orders"):
            st.session_state.page = "Track"

    with c2:
        if st.button("📜 Order History"):
            st.session_state.page = "History"

    with c3:
        if st.button("⭐ Reviews"):
            st.session_state.page = "Review"


# TRACK ORDER SCREEN
def track_screen():

    st.title("📍 Track Orders")

    query = """
    SELECT * FROM orders
    WHERE customer_name=%s
    """

    cursor.execute(query, (st.session_state.username,))

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=[
                "ID",
                "Customer",
                "Pickup",
                "Drop",
                "Package",
                "Status",
                "Driver",
                "Date"
            ]
        )

        st.dataframe(df)

        st.map(pd.DataFrame({
            'lat': [13.0827],
            'lon': [80.2707]
        }))

    else:
        st.warning("No Orders Found")


# ORDER HISTORY
def history_screen():

    st.title("📜 Order History")

    query = """
    SELECT * FROM orders
    WHERE customer_name=%s
    """

    cursor.execute(query, (st.session_state.username,))

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Customer",
            "Pickup",
            "Drop",
            "Package",
            "Status",
            "Driver",
            "Date"
        ]
    )

    st.dataframe(df)


# REVIEW SCREEN
def review_screen():

    st.title("⭐ Rating & Review")

    rating = st.slider("Rate Service", 1, 5)

    review = st.text_area("Write Review")

    if st.button("Submit Review"):

        query = """
        INSERT INTO reviews(
            customer_name,
            rating,
            review
        )
        VALUES(%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                st.session_state.username,
                rating,
                review
            )
        )

        db.commit()

        st.success("Review Submitted Successfully")


# DRIVER DASHBOARD
def driver_dashboard():

    st.title("🚗 Driver Dashboard")

    st.success("Status : Online")

    query = """
    SELECT * FROM orders
    WHERE assigned_driver=%s
    OR assigned_driver='Not Assigned'
    """

    cursor.execute(query, (st.session_state.username,))

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Customer",
            "Pickup",
            "Drop",
            "Package",
            "Status",
            "Driver",
            "Date"
        ]
    )

    st.dataframe(df)

    st.markdown("---")

    order_id = st.number_input("Enter Order ID", step=1)

    status = st.selectbox(
        "Update Status",
        [
            "Picked Up",
            "On The Way",
            "Delivered"
        ]
    )

    if st.button("Update Delivery Status"):

        query = """
        UPDATE orders
        SET status=%s,
        assigned_driver=%s
        WHERE id=%s
        """

        cursor.execute(
            query,
            (
                status,
                st.session_state.username,
                order_id
            )
        )

        db.commit()

        st.success("Status Updated Successfully")

    st.markdown("---")

    st.metric(
        label="Today's Earnings",
        value="₹2500"
    )


# ADMIN DASHBOARD
def admin_dashboard():

    st.title("🏢 Admin Dashboard")

    st.subheader("📦 All Orders")

    cursor.execute("SELECT * FROM orders")

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Customer",
            "Pickup",
            "Drop",
            "Package",
            "Status",
            "Driver",
            "Date"
        ]
    )

    st.dataframe(df)

    st.markdown("---")

    st.subheader("👥 Users")

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    users_df = pd.DataFrame(
        users,
        columns=[
            "ID",
            "Username",
            "Password",
            "Role"
        ]
    )

    st.dataframe(users_df)

    st.markdown("---")

    st.subheader("📊 Analytics")

    total_orders = len(data)

    delivered = len(
        [x for x in data if x[5] == "Delivered"]
    )

    pending = total_orders - delivered

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Orders", total_orders)

    with c2:
        st.metric("Delivered", delivered)

    with c3:
        st.metric("Pending", pending)

    st.markdown("---")

    st.subheader("Assign Driver")

    order_id = st.number_input(
        "Order ID",
        step=1,
        key="admin_order"
    )

    driver_name = st.text_input("Driver Username")

    if st.button("Assign Driver"):

        query = """
        UPDATE orders
        SET assigned_driver=%s
        WHERE id=%s
        """

        cursor.execute(
            query,
            (
                driver_name,
                order_id
            )
        )

        db.commit()

        st.success("Driver Assigned Successfully")


# ---------------- PAGE ROUTING ----------------

if st.session_state.page == "Splash":
    splash_screen()

elif st.session_state.page == "Onboarding":
    onboarding_screen()

elif st.session_state.page == "Login":
    login_screen()

elif st.session_state.page == "Home":
    home_screen()

elif st.session_state.page == "Track":
    track_screen()

elif st.session_state.page == "History":
    history_screen()

elif st.session_state.page == "Review":
    review_screen()

elif st.session_state.page == "Driver Dashboard":
    driver_dashboard()

elif st.session_state.page == "Admin Dashboard":
    admin_dashboard()
