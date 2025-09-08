import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

# Καθαρισμός whitespace στα ονόματα στηλών
users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Συναρτήσεις -----------------
def is_latin(s):
    return all(ord(c) < 128 for c in str(s))

def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_row = users_df[
            ((users_df['username'] == username_or_email) |
             (users_df['E-mail'] == username_or_email)) &
            (users_df['password'] == password)
        ]

        if not user_row.empty:
            st.session_state["user"] = user_row.iloc[0].to_dict()
            st.session_state["page"] = "recommendations"
            st.session_state["welcome_shown"] = False  # reset welcome
        else:
            st.error("❌ Λάθος Username/E-mail ή Κωδικός")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again"):
                    st.session_state["page"] = "login"
            with col2:
                user_check = users_df[
                    (users_df['username'] == username_or_email) |
                    (users_df['E-mail'] == username_or_email)
                ]
                if not user_check.empty:
                    if st.button("📧 Recover Password"):
                        st.info(f"Enter your email to reset password.")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    errors = []

    # ----------------- Inputs -----------------
    new_user["username"] = st.text_input("Choose a username")
    if new_user["username"] == "" or not is_latin(new_user["username"]):
        errors.append("Username")

    new_user["E-mail"] = st.text_input("E-mail")
    if new_user["E-mail"] == "" or not is_latin(new_user["E-mail"]):
        errors.append("E-mail")

    new_user["password"] = st.text_input("Password", type="password")
    if new_user["password"] == "":
        errors.append("Password")

    new_user["first_name"] = st.text_input("First name")
    if new_user["first_name"] == "" or not is_latin(new_user["first_name"]):
        errors.append("First Name")

    new_user["last_name"] = st.text_input("Last name")
    if new_user["last_name"] == "" or not is_latin(new_user["last_name"]):
        errors.append("Last Name")

    # Date of birth
    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990, 1, 1),
                                    min_value=datetime(1, 1, 1),
                                    max_value=datetime.now())

    # Choose city from Greece
    cities = ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Volos", "Ioannina", "Chania"]
    new_user["city"] = st.selectbox("City of Residence", cities)

    # Choose profession
    professions = ["Student", "Teacher", "Engineer", "Doctor", "Artist", "Freelancer", "Retired", "Entrepreneur"]
    new_user["profession"] = st.selectbox("Profession", professions)

    # Interests (multi-select)
    interests_list = ["Fitness", "Travel", "Technology", "Cooking", "Gaming", "Music", "Photography", "Reading", "Art", "Sports"]
    new_user["interests"] = st.multiselect("What are your main interests? (Choose up to 5)", interests_list)

    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])

    lifestyle_list = ["Outdoor", "Indoor", "Social", "Solitary", "Family-oriented", "Work-focused", "Travel-loving", "Fitness-focused"]
    new_user["lifestyle"] = st.multiselect("Lifestyle Preferences (Choose up to 5)", lifestyle_list)

    goals_list = ["Health", "Education", "Career", "Creativity", "Entertainment", "Productivity", "Financial", "Travel"]
    new_user["goals"] = st.multiselect("Your Goals (Choose up to 5)", goals_list)

    devices_list = ["iPhone", "Android Phone", "iPad", "Laptop", "Desktop", "Mac", "PC", "Camera", "Smartwatch"]
    new_user["devices_owned"] = st.multiselect("Devices you own", devices_list)

    if st.button("Create Account"):
        if errors:
            st.error(f"❌ Please fill correctly: {', '.join(errors)}")
        else:
            global users_df
            users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
            st.success("🎉 Account created successfully! Please login.")
            st.session_state["page"] = "login"

def recommendations():
    user = st.session_state["user"]

    # ----------------- Welcome Message -----------------
    if not st.session_state.get("welcome_shown", False):
        placeholder = st.empty()
        placeholder.success(f"🎉 Welcome {user['first_name']}! Here are suggestions for you!")
        time.sleep(3)
        placeholder.empty()
        st.session_state["welcome_shown"] = True

    st.markdown("## 🎯 Personalized Recommendations")
    
    # Filter recommendations
    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    # ----------------- Products -----------------
    product_recs = recs[recs['category'].str.lower().str.contains("product")].head(2)
    if not product_recs.empty:
        st.markdown("### 🛍️ Products")
        cols = st.columns(len(product_recs))
        for idx, (_, row) in enumerate(product_recs.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                    <div style="padding:15px; border:1px solid #eee; border-radius:10px; box-shadow: 2px 2px 5px #ddd;">
                        <h4 style="color:#4CAF50;">{row['name']}</h4>
                        <p>💰 Price: {row['price']} €</p>
                        <p>📌 Category: {row['category']}</p>
                        <a href="{row['url']}" target="_blank">🔗 Learn more</a>
                    </div>
                    """, unsafe_allow_html=True)
                if st.button(f"➕ Add {row['name']} to Cart", key=row["id"]):
                    st.success(f"✅ {row['name']} added to cart!")

    # ----------------- Services -----------------
    service_recs = recs[recs['category'].str.lower().str.contains("service")].head(2)
    if not service_recs.empty:
        st.markdown("### 🛠️ Services")
        cols = st.columns(len(service_recs))
        for idx, (_, row) in enumerate(service_recs.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                    <div style="padding:15px; border:1px solid #eee; border-radius:10px; box-shadow: 2px 2px 5px #ddd;">
                        <h4 style="color:#2196F3;">{row['name']}</h4>
                        <p>📌 Category: {row['category']}</p>
                        <a href="{row['url']}" target="_blank">🔗 Learn more</a>
                    </div>
                    """, unsafe_allow_html=True)

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





