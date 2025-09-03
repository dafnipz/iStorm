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

# ----------------- Helpers -----------------
def is_latin(s):
    try:
        s.encode('latin1')
    except UnicodeEncodeError:
        return False
    return True

# ----------------- Login -----------------
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
            # Show welcome message for 3 seconds
            st.success(f"🎉 Welcome {st.session_state['user']['first_name']}!")
            time.sleep(3)
            st.session_state["page"] = "recommendations"
        else:
            st.error("❌ Wrong Username/E-mail or Password")
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
                    st.info("📧 Recover Password feature coming soon.")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

# ----------------- Sign up -----------------
def signup():
    st.markdown("## 📝 Sign Up")
    new_user = {}

    new_user["username"] = st.text_input("Choose a username (latin only)")
    new_user["E-mail"] = st.text_input("E-mail (latin only)")
    new_user["password"] = st.text_input("Password", type="password")
    new_user["first_name"] = st.text_input("First name (latin only)")
    new_user["last_name"] = st.text_input("Last name (latin only)")
    new_user["dob"] = st.date_input("Date of Birth",
                                    value=datetime(1990, 1, 1),
                                    min_value=datetime(1, 1, 1),
                                    max_value=datetime.now())
    # Predefined lists
    cities = ["Athens","Thessaloniki","Patras","Heraklion","Larissa","Volos","Ioannina","Chania","Rhodes"]
    professions = ["Engineer","Doctor","Teacher","Student","Artist","Entrepreneur","Developer","Designer"]
    budgets = ["low","medium","high"]
    tech_levels = ["beginner","intermediate","advanced"]
    interests_list = ["Fitness","Travel","Music","Reading","Cooking","Photography","Gaming","Sports","Technology","Art"]
    lifestyle_list = ["Outdoor","Indoor","Social","Introvert","Active","Relaxed","Creative","Adventurous","Organized","Flexible"]
    goals_list = ["Health","Career","Education","Travel","Creativity","Productivity","Finance","Entertainment","Networking","Self-improvement"]
    devices_list = ["iPhone","Mac","iPad","PC","Camera","Smartwatch","Headphones","Tablet","Laptop","Other"]

    new_user["city"] = st.selectbox("City", cities)
    new_user["profession"] = st.selectbox("Profession", professions)
    new_user["interests"] = st.multiselect("What interests you most? (pick up to 5)", interests_list, max_selections=5)
    new_user["budget"] = st.selectbox("Budget", budgets)
    new_user["tech_level"] = st.selectbox("Tech Level", tech_levels)
    new_user["lifestyle"] = st.multiselect("Lifestyle Preferences", lifestyle_list, max_selections=5)
    new_user["goals"] = st.multiselect("Your Goals", goals_list, max_selections=5)
    new_user["devices_owned"] = st.multiselect("Devices you own", devices_list, max_selections=5)

    # Validation
    all_fields_filled = all([
        new_user["username"], new_user["E-mail"], new_user["password"],
        new_user["first_name"], new_user["last_name"], new_user["dob"],
        new_user["city"], new_user["profession"], new_user["interests"],
        new_user["budget"], new_user["tech_level"], new_user["lifestyle"],
        new_user["goals"], new_user["devices_owned"]
    ])
    latin_fields = all(is_latin(str(new_user[k])) for k in ["username","E-mail","first_name","last_name"])

    if st.button("Create Account"):
        if not all_fields_filled:
            st.error("❌ All fields are required!")
        elif not latin_fields:
            st.error("❌ Only Latin characters allowed in username, email, first and last name.")
        else:
            global users_df
            # Convert lists to comma-separated strings
            for key in ["interests","lifestyle","goals","devices_owned"]:
                new_user[key] = ",".join(new_user[key])
            users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
            st.success("🎉 Account created successfully! Please login.")
            st.session_state["page"] = "login"

# ----------------- Recommendations -----------------
def recommendations():
    st.markdown("<div style='text-align: right;'>🔒 <button onclick=''>Logout</button></div>", unsafe_allow_html=True)
    user = st.session_state["user"]

    st.markdown(f"## Welcome {user['first_name']}! Here's your personalized suggestions:")

    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    # Split into products and services
    products = recs[recs['category'].str.lower() == "product"]
    services = recs[recs['category'].str.lower() == "service"]

    # Display two columns for products
    prod_cols = st.columns(2)
    for i, (_, row) in enumerate(products.head(2).iterrows()):
        with prod_cols[i%2]:
            st.image(row["image_url"] if "image_url" in row else "", use_column_width=True)
            st.subheader(row["name"])
            st.write(f"💰 Price: {row['price']} €")
            st.write(f"📌 Category: {row['category']}")

    # Display two columns for services below products
    serv_cols = st.columns(2)
    for i, (_, row) in enumerate(services.head(2).iterrows()):
        with serv_cols[i%2]:
            st.subheader(row["name"])
            st.write(f"💰 Price: {row['price']} €")
            st.write(f"📌 Category: {row['category']}")

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login()
elif st.session_state["page"] == "signup":
    signup()
elif st.session_state["page"] == "recommendations":
    recommendations()
