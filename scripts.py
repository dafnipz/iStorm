import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Συναρτήσεις -----------------
def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email", key="login_input")
    password = st.text_input("Password", type="password", key="login_pass")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Προσπάθησε ξανά"):
            st.session_state["page"] = "login"
    with col2:
        if st.button("📧 Ανάκτηση Κωδικού"):
            st.session_state["page"] = "recover_password"

    if st.button("Login", key="login_button"):
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

    st.markdown("---")
    st.write("Not signed up yet?")
    if st.button("👉 Sign up"):
        st.session_state["page"] = "signup"

def recover_password():
    st.markdown("## 🔑 Recover Password")
    email = st.text_input("Enter your registered email", key="recover_email")
    if st.button("Send recovery link"):
        user_row = users_df[users_df['E-mail'] == email]
        if not user_row.empty:
            st.success("📧 Έχουμε στείλει ένα link στο email σου (υποθετικό).")
            st.session_state["recover_user"] = email
            st.session_state["page"] = "reset_password"
        else:
            st.error("❌ Email δεν βρέθηκε!")

def reset_password():
    st.markdown("## 🔑 Set New Password")
    new_pass = st.text_input("New Password", type="password", key="new_pass")
    confirm_pass = st.text_input("Confirm New Password", type="password", key="confirm_pass")

    if st.button("Reset Password"):
        if new_pass != confirm_pass:
            st.error("❌ Οι κωδικοί δεν ταιριάζουν!")
        else:
            email = st.session_state.get("recover_user")
            users_df.loc[users_df['E-mail'] == email, 'password'] = new_pass
            st.success("✅ Ο κωδικός άλλαξε επιτυχώς! Κάνε login με τον νέο κωδικό.")
            st.session_state["page"] = "login"

def signup():
    st.markdown("## 📝 Sign Up")

    new_user = {}
    new_user["username"] = st.text_input("Choose a username")
    new_user["E-mail"] = st.text_input("Email")
    new_user["password"] = st.text_input("Password", type="password")
    new_user["first_name"] = st.text_input("First name")
    new_user["last_name"] = st.text_input("Last name")
    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990, 1, 1),
                                    min_value=datetime(1, 1, 1),
                                    max_value=datetime.now())
    new_user["city"] = st.text_input("City")
    new_user["profession"] = st.text_input("Profession")
    new_user["interests"] = st.text_area("Interests (comma separated)")
    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])
    new_user["lifestyle"] = st.text_area("Lifestyle (comma separated)")
    new_user["goals"] = st.text_area("Goals (comma separated)")
    new_user["devices_owned"] = st.text_area("Devices Owned (comma separated)")

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
elif st.session_state["page"] == "recover_password":
    recover_password()
elif st.session_state["page"] == "reset_password":
    reset_password()
elif st.session_state["page"] == "recommendations":
    recommendations()









