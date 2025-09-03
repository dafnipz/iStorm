import streamlit as st
import pandas as pd
from datetime import datetime
import re

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

# Καθαρισμός whitespace στα ονόματα στηλών
users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Validation -----------------
def validate_user_input(user):
    missing = [k for k,v in user.items() if v==""]
    nonlatin = [k for k,v in user.items() if not re.match(r'^[A-Za-z0-9, @._-]*$', str(v))]
    return missing, nonlatin

# ----------------- Συναρτήσεις -----------------
def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
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
                st.error("❌ Wrong Username/Email or Password")
                st.session_state["recover_visible"] = True

    with col2:
        if st.session_state.get("recover_visible", False):
            st.warning("Forgot your password?")
            if st.button("📧 Recover password"):
                username_email_input = st.text_input("Enter your email to recover")
                if username_email_input:
                    user_check = users_df[users_df['E-mail'] == username_email_input]
                    if not user_check.empty:
                        st.success(f"Recovery email sent to: {username_email_input}")
                    else:
                        st.error("Email not found!")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    new_user["username"] = st.text_input("Choose a username")
    new_user["E-mail"] = st.text_input("Email")
    new_user["password"] = st.text_input("Password", type="password")
    new_user["first_name"] = st.text_input("First name")
    new_user["last_name"] = st.text_input("Last name")
    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990, 1, 1),
                                    min_value=datetime(1,1,1),
                                    max_value=datetime.now())
    
    # Dropdown πόλης
    greek_cities = ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa",
                    "Volos", "Ioannina", "Chania", "Rhodes", "Kavala", "Kalamata",
                    "Corfu", "Agrinio", "Trikala", "Chios", "Mytilene"]
    new_user["city"] = st.selectbox("City", greek_cities)
    
    # Dropdown επαγγέλματος
    professions = ["Software Engineer", "Doctor", "Teacher", "Student", "Artist",
                   "Photographer", "Engineer", "Designer", "Chef", "Musician",
                   "Writer", "Researcher", "Entrepreneur", "Consultant", "Nurse"]
    new_user["profession"] = st.selectbox("Profession", professions)
    
    st.markdown("### What are your main interests? (Choose up to 5)")
    interests_options = ["fitness", "travel", "tech", "music", "art", "photography",
                         "gaming", "reading", "fashion", "food"]
    selected_interests = st.multiselect("", interests_options, max_selections=5)
    new_user["interests"] = ",".join(selected_interests)
    
    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])
    
    new_user["lifestyle"] = st.text_area("Lifestyle Preferences (comma separated, latin characters only)")
    new_user["goals"] = st.text_area("Your goals (comma separated, latin characters only)")
    new_user["devices_owned"] = st.text_area("Devices you own (comma separated, latin characters only)")

    if st.button("Create Account"):
        missing, nonlatin = validate_user_input(new_user)
        if missing:
            st.error(f"⚠️ Please fill all fields: {', '.join(missing)}")
            return
        if nonlatin:
            st.error(f"⚠️ Only latin characters allowed in: {', '.join(nonlatin)}")
            return
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


