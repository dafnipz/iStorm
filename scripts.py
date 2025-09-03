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
def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Έλεγχος χρήστη με username ή email
        user_row = users_df[
            ((users_df['username'] == username_or_email) |
             (users_df['E-mail'] == username_or_email)) &
            (users_df['password'] == password)
        ]

        if not user_row.empty:
            st.session_state["user"] = user_row.iloc[0].to_dict()
            st.session_state["page"] = "recommendations"
            st.session_state["welcome_shown"] = False  # για να εμφανιστεί το welcome message
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

def recommendations():
    user = st.session_state["user"]

    # ----------------- Welcome Message 3 δευτ -----------------
    if not st.session_state.get("welcome_shown", False):
        placeholder = st.empty()
        placeholder.success(f"🎉 Welcome {user['first_name']}! Let's find your perfect match!")
        time.sleep(3)
        placeholder.empty()
        st.session_state["welcome_shown"] = True

    st.markdown("## 🎯 Personalized Recommendations")
    st.write(f"Hello {user['first_name']} 👋, here are your suggestions:")

    # Φιλτράρισμα προϊόντων και υπηρεσιών
    recs = products_df[
        (products_df['target_profession'].isin([user["profession"], "All"])) |
        (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(","))))
    ]

    if recs.empty:
        st.info("Δεν βρέθηκαν προτάσεις για εσένα 🙁")
    else:
        # Εμφάνιση 2 προϊόντων και 2 υπηρεσιών
        product_count, service_count = 0, 0
        for _, row in recs.iterrows():
            if "product" in row['category'].lower() and product_count < 2:
                st.subheader(row["name"])
                st.write(f"💰 Price: {row['price']} €")
                st.write(f"📌 Category: {row['category']}")
                st.markdown(f"[🔗 Learn more]({row['url']})")
                product_count += 1
            elif "service" in row['category'].lower() and service_count < 2:
                st.subheader(row["name"])
                st.write(f"📌 Category: {row['category']}")
                st.markdown(f"[🔗 Learn more]({row['url']})")
                service_count += 1
            if product_count >= 2 and service_count >= 2:
                break

    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"

# ----------------- Navigation -----------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login()
elif st.session_state["page"] == "signup":
    # εδώ μπαίνει η signup function σου
    pass
elif st.session_state["page"] == "recommendations":
    recommendations()













