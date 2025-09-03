import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

# Καθαρισμός whitespace στα ονόματα στηλών
users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Συναρτήσεις -----------------
def login():
    st.markdown("## 👋 Welcome (back)")

    username_or_email = st.text_input("Username or Email", help="Enter your username or email to login")
    password = st.text_input("Password", type="password", help="Enter your password")

    col1, col2 = st.columns(2)
    with col1:
        login_btn = st.button("Login")
    with col2:
        recover_btn = st.button("Recover Password")

    if login_btn:
        user_row = users_df[
            ((users_df['username'] == username_or_email) |
             (users_df['E-mail'] == username_or_email)) &
            (users_df['password'] == password)
        ]

        if not user_row.empty:
            st.session_state["user"] = user_row.iloc[0].to_dict()
            st.success(f"✅ Welcome {st.session_state['user']['first_name']}!")
            st.session_state["page"] = "recommendations"
        else:
            st.error("❌ Wrong Username/E-mail or Password")

    if recover_btn:
        st.info("Enter your email to recover your password:")
        recover_email = st.text_input("Email")
        if st.button("Send Recovery Link"):
            user_check = users_df[users_df['E-mail'] == recover_email]
            if not user_check.empty:
                st.success(f"📧 Recovery link sent to: {recover_email}")
            else:
                st.warning("⚠️ Email not found in our database.")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    new_user["username"] = st.text_input("Choose a username", help="The username you'll use to log in")
    new_user["E-mail"] = st.text_input("Email", help="Provide a valid email for password recovery")
    new_user["password"] = st.text_input("Password", type="password", help="Choose a strong password")
    new_user["first_name"] = st.text_input("First name", help="Your first name")
    new_user["last_name"] = st.text_input("Last name", help="Your last name")
    new_user["dob"] = st.date_input(
        "Date of Birth", 
        value=datetime(1990, 1, 1),
        min_value=datetime(1, 1, 1),
        max_value=datetime.now(),
        help="Your birth date"
    )
    new_user["city"] = st.text_input("City", help="Where do you live?")
    new_user["profession"] = st.text_input("Profession", help="Your current profession")

    new_user["interests"] = st.multiselect(
        "What are your main interests? (Choose up to 5)",
        options=["Fitness", "Travel", "Tech", "Music", "Reading", "Photography", "Art", "Gaming", "Cooking", "Fashion"],
        help="Select up to 5 topics that interest you"
    )

    new_user["lifestyle"] = st.multiselect(
        "What best describes your lifestyle? (Choose up to 3)",
        options=["Office work", "Home-based", "Outdoor sports", "Travel frequently", "Student", "Freelancer", "Entrepreneur"],
        help="Select up to 3 lifestyle types"
    )

    new_user["goals"] = st.multiselect(
        "What are your main goals? (Choose up to 3)",
        options=["Productivity", "Health", "Creativity", "Learning", "Entertainment", "Travel", "Networking"],
        help="Select up to 3 personal goals"
    )

    new_user["devices_owned"] = st.multiselect(
        "Which devices do you own?",
        options=["iPhone", "Mac", "iPad", "Apple Watch", "AirPods", "Camera", "Windows PC", "Android phone", "Tablet", "Other"],
        help="Select all devices you currently own"
    )

    new_user["budget"] = st.selectbox(
        "Budget", 
        ["Low", "Medium", "High"],
        help="Your preferred price range for products"
    )

    new_user["tech_level"] = st.selectbox(
        "Tech Level", 
        ["Beginner", "Intermediate", "Advanced"],
        help="Your level of technology expertise"
    )

    if st.button("Create Account"):
        global users_df
        users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
        st.success("🎉 Account created successfully! Please login.")
        st.session_state["page"] = "login"

def recommendations():
    st.markdown("## 🎯 Personalized Recommendations")
    user = st.session_state["user"]
    st.write(f"Hello {user['first_name']} 👋, here are your suggestions:")

    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    if recs.empty:
        st.info("No recommendations found for you 🙁")
    else:
        for _, row in recs.iterrows():
            st.subheader(row["name"])
            st.write(f"💰 Price: {row['price']} €")
            st.write(f"📌 Category: {row['category']}")
            st.markdown(f"[🔗 Learn more]({row['url']})")
            if st.button(f"➕ Add {row['name']} to Cart", key=row["id"]):
                st.success(f"✅ {row['name']} added to cart!")

    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login()
elif st.session_state["page"] == "signup":
    signup()
elif st.session_state["page"] == "recommendations":
    recommendations()
