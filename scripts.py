import streamlit as st
import pandas as pd
from datetime import datetime
import re

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Βοηθητικές συναρτήσεις -----------------
def is_latin(s):
    return bool(re.match(r'^[A-Za-z0-9@.,:;!?() \-]*$', s))

def validate_user_input(user):
    required_fields = ["username","email","password","first_name","last_name","dob",
                       "city","profession","interests","budget","tech_level","lifestyle",
                       "goals","devices_owned"]
    for field in required_fields:
        if field not in user or user[field] in ["", None]:
            return False, f"Field '{field}' cannot be empty!"
        if field not in ["dob","budget","tech_level","city","profession"] and not is_latin(str(user[field])):
            return False, f"Only Latin characters allowed in: {field}"
    return True, ""

# ----------------- Login -----------------
def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        login_btn = st.button("Login")
    with col2:
        signup_btn = st.button("👉 Sign up")

    if signup_btn:
        st.session_state["page"] = "signup"
        return

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
            st.error("❌ Λάθος Username/E-mail ή Κωδικός")
            # recover password εμφανίζεται μόνο αν υπάρχει χρήστης
            user_check = users_df[
                (users_df['username'] == username_or_email) |
                (users_df['E-mail'] == username_or_email)
            ]
            col3, col4 = st.columns(2)
            with col3:
                if st.button("🔄 Προσπάθησε ξανά"):
                    st.experimental_rerun()
            with col4:
                if not user_check.empty:
                    if st.button("📧 Ανάκτηση Κωδικού"):
                        email = user_check.iloc[0]['E-mail']
                        st.info(f"Σου στείλαμε mail στο: {email}")
                else:
                    st.info("Ο χρήστης δεν βρέθηκε. Θέλεις να κάνεις εγγραφή;")

# ----------------- Sign-up -----------------
def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    new_user["username"] = st.text_input("Choose a username")
    new_user["E-mail"] = st.text_input("E-mail")
    new_user["password"] = st.text_input("Password", type="password")
    new_user["first_name"] = st.text_input("First name")
    new_user["last_name"] = st.text_input("Last name")
    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990, 1, 1),
                                    min_value=datetime(1,1,1), max_value=datetime.now())
    # Dropdown επιλογές πόλης και επαγγέλματος
    cities = ["Athens","Thessaloniki","Heraklion","Larisa","Patras","Kavala","Rhodes","Corfu","Volos","Ioannina"]
    professions = ["Software Engineer","Teacher","Designer","Diver","Photographer","Marketing Specialist",
                   "Student","Entrepreneur","Freelancer","Doctor","Nurse","Artist","Writer"]
    new_user["city"] = st.selectbox("City", cities)
    new_user["profession"] = st.selectbox("Profession", professions)

    # Multi-select fields
    interests_options = ["Fitness","Travel","Tech","Reading","Art","Music","Photography","Gaming","Fashion","Outdoors"]
    lifestyle_options = ["Office work","Home","Outdoor sports","Travel","Creativity","Productivity","Health","Learning"]
    goals_options = ["Health","Entertainment","Education","Career","Wealth","Creativity","Productivity","Learning"]
    devices_options = ["iPhone","iPad","Mac","Apple Watch","AirPods","Camera","Laptop","Tablet","Smartwatch"]

    new_user["interests"] = ",".join(st.multiselect("What interests you most? Choose up to 5", interests_options, max_selections=5))
    new_user["budget"] = st.selectbox("Budget", ["low","medium","high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner","intermediate","advanced"])
    new_user["lifestyle"] = ",".join(st.multiselect("Lifestyle preferences (max 5)", lifestyle_options, max_selections=5))
    new_user["goals"] = ",".join(st.multiselect("Your goals (max 5)", goals_options, max_selections=5))
    new_user["devices_owned"] = ",".join(st.multiselect("Devices you own (max 5)", devices_options, max_selections=5))

    if st.button("Create Account"):
        valid, msg = validate_user_input(new_user)
        if not valid:
            st.error(f"⚠️ {msg}")
        else:
            global users_df
            users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
            st.success("🎉 Account created successfully! Please login.")
            st.session_state["page"] = "login"

# ----------------- Recommendations -----------------
def recommendations():
    st.markdown("## 🎯 Personalized Recommendations")

    user = st.session_state["user"]
    st.write(f"Hello {user['first_name']} 👋, here are your suggestions:")

    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    if recs.empty:
        st.info("Δεν βρέθηκαν προτάσεις για εσένα 🙁")
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







