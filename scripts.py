import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

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
            st.session_state["welcome_shown"] = False
        else:
            st.error("❌ Λάθος Username/E-mail ή Κωδικός")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

def signup():
    st.markdown("## 📝 Sign Up")
    new_user = {}
    errors = []

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

    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990,1,1),
                                    min_value=datetime(1,1,1), max_value=datetime.now())

    cities = ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Volos", "Ioannina", "Chania"]
    new_user["city"] = st.selectbox("City of Residence", cities)

    professions = ["Student", "Teacher", "Engineer", "Doctor", "Artist", "Freelancer", "Retired", "Entrepreneur"]
    new_user["profession"] = st.selectbox("Profession", professions)

    interests_list = ["Fitness", "Travel", "Technology", "Cooking", "Gaming", "Music", "Photography", "Reading", "Art", "Sports"]
    new_user["interests"] = st.multiselect("Main interests (up to 5)", interests_list)

    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])

    lifestyle_list = ["Outdoor", "Indoor", "Social", "Solitary", "Family-oriented", "Work-focused", "Travel-loving", "Fitness-focused"]
    new_user["lifestyle"] = st.multiselect("Lifestyle Preferences (up to 5)", lifestyle_list)

    goals_list = ["Health", "Education", "Career", "Creativity", "Entertainment", "Productivity", "Financial", "Travel"]
    new_user["goals"] = st.multiselect("Goals (up to 5)", goals_list)

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

    if not st.session_state.get("welcome_shown", False):
        placeholder = st.empty()
        placeholder.success(f"🎉 Welcome {user['first_name']}! Here are suggestions for you!")
        time.sleep(2)
        placeholder.empty()
        st.session_state["welcome_shown"] = True

    st.markdown("## 🎯 Personalized Recommendations")
    
    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    st.markdown("### 🛍️ Products Demo")
    for _, row in recs.head(3).iterrows():
        st.markdown(f"- **{row['name']}** ({row['category']}) - {row['price']} €")
    
    st.markdown("---")
    if st.button("🔍 Browse Apple Products Demo"):
        st.session_state["page"] = "apple_browser"
    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"

def apple_browsing():
    st.markdown("## 🍏 Apple Product Browser Demo")
    query = st.text_input("Search Apple Product", "iPhone 15")

    # Demo results (στατικά links)
    apple_demo = [
        {"name": "iPhone 15 Pro", "site": "Apple Store", "url": "https://www.apple.com/gr/iphone-15-pro/"},
        {"name": "MacBook Air M2", "site": "Apple Store", "url": "https://www.apple.com/gr/macbook-air-m2/"},
        {"name": "iPad Pro 12.9", "site": "Apple Store", "url": "https://www.apple.com/gr/ipad-pro/"}
    ]

    st.markdown(f"### Results for '{query}':")
    for item in apple_demo:
        st.markdown(f"- **{item['name']}** ({item['site']}) [Link]({item['url']})")

    st.markdown("---")
    if st.button("🔙 Back to Recommendations"):
        st.session_state["page"] = "recommendations"

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login()
elif st.session_state["page"] == "signup":
    signup()
elif st.session_state["page"] == "recommendations":
    recommendations()
elif st.session_state["page"] == "apple_browser":
    apple_browsing()





