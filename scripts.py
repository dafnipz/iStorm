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
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_button"):
        # Έλεγχος χρήστη με username ή email
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

            # Κουμπιά δίπλα-δίπλα
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Προσπάθησε ξανά", key="try_again"):
                    st.session_state["page"] = "login"

            with col2:
                user_check = users_df[
                    (users_df['username'] == username_or_email) |
                    (users_df['E-mail'] == username_or_email)
                ]
                if not user_check.empty:
                    if st.button("📧 Ανάκτηση Κωδικού", key="recover_password"):
                        st.info(f"Σου στείλαμε mail στο: {user_check.iloc[0]['E-mail']}")

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up", key="signup_redirect"):
        st.session_state["page"] = "signup"

def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    new_user["username"] = st.text_input("Choose a username", key="signup_username")
    new_user["E-mail"] = st.text_input("Email", key="signup_email")
    new_user["password"] = st.text_input("Password", type="password", key="signup_password")
    new_user["first_name"] = st.text_input("First name", key="signup_first")
    new_user["last_name"] = st.text_input("Last name", key="signup_last")
    new_user["dob"] = st.date_input(
        "Date of Birth", 
        value=datetime(1990, 1, 1),
        min_value=datetime(1, 1, 1),
        max_value=datetime.now(),
        key="signup_dob"
    )
    new_user["city"] = st.text_input("City", key="signup_city")
    new_user["profession"] = st.text_input("Profession", key="signup_prof")
    new_user["interests"] = st.text_area("Interests (comma separated)", key="signup_interests")
    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"], key="signup_budget")
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"], key="signup_tech")
    new_user["lifestyle"] = st.text_area("Lifestyle (comma separated)", key="signup_lifestyle")
    new_user["goals"] = st.text_area("Goals (comma separated)", key="signup_goals")
    new_user["devices_owned"] = st.text_area("Devices Owned (comma separated)", key="signup_devices")

    if st.button("Create Account", key="create_account"):
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
        st.info("Δεν βρέθηκαν προτάσεις για εσένα 🙁")
    else:
        for _, row in recs.iterrows():
            st.subheader(row["name"])
            st.write(f"💰 Price: {row['price']} €")
            st.write(f"📌 Category: {row['category']}")
            st.markdown(f"[🔗 Learn more]({row['url']})")
            if st.button(f"➕ Add {row['name']} to Cart", key=row["id"]):
                st.success(f"✅ {row['name']} added to cart!")

    if st.button("🔒 Logout", key="logout"):
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







