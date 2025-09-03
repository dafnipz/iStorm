import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------- Φόρτωση δεδομένων -----------------
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/refs/heads/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=";")
products_df = pd.read_csv(products_file, sep=";")

# Καθαρισμός whitespace στα ονόματα στηλών
users_df.columns = users_df.columns.str.strip()
products_df.columns = products_df.columns.str.strip()

# ----------------- Helper Functions -----------------
def is_latin(s):
    return all(ord(c) < 128 for c in s)

def validate_user_input(user):
    errors = []
    for key, value in user.items():
        if not value:
            errors.append(f"Missing field: {key}")
        elif key in ['username', 'email', 'first_name', 'last_name', 'interests', 'lifestyle', 'goals', 'devices_owned', 'dob']:
            if not is_latin(str(value)):
                errors.append(f"Only latin characters allowed in: {key}")
    return errors

# ----------------- Συναρτήσεις -----------------
import streamlit as st
import time

def login():
    st.markdown("## 👋 Welcome (back)")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    login_clicked = st.button("Login")

    if login_clicked:
        user_row = users_df[
            ((users_df['username'] == username_or_email) |
             (users_df['E-mail'] == username_or_email)) &
            (users_df['password'] == password)
        ]

        if not user_row.empty:
            st.session_state["user"] = user_row.iloc[0].to_dict()
            
            # Προσωρινό μήνυμα καλωσορίσματος
            placeholder = st.empty()
            placeholder.success(f"🎉 Welcome {st.session_state['user']['first_name']}! Redirecting to your recommendations...")
            st.session_state["page"] = "recommendations"
            time.sleep(3)
            placeholder.empty()
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
                    st.warning("Forgot your password?")
                    email_input = st.text_input("Enter your email to reset password")
                    if st.button("📧 Send Reset Link"):
                        st.info(f"A password reset link has been sent to: {email_input}")

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

    # Date picker with large range
    new_user["dob"] = st.date_input("Date of Birth", value=datetime(1990, 1, 1),
                                    min_value=datetime(1, 1, 1),
                                    max_value=datetime.now())

    # Dropdowns for city and profession
    greek_cities = ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Rhodes", "Kavala", "Corfu"]
    professions = ["Software Engineer", "Teacher", "Diver", "Designer", "Photographer", "Marketing Specialist", "Entrepreneur", "Student", "Freelancer", "Doctor", "Lawyer"]

    new_user["city"] = st.selectbox("Choose your city", greek_cities)
    new_user["profession"] = st.selectbox("Choose your profession", professions)

    # Interests, budget, tech level, lifestyle, goals, devices
    interest_options = ["Fitness", "Travel", "Tech", "Music", "Reading", "Art", "Fashion", "Photography", "Gaming", "Food"]
    new_user["interests"] = ", ".join(st.multiselect("What interests you most? Choose up to 5", interest_options, max_selections=5))

    new_user["budget"] = st.selectbox("Budget", ["low", "medium", "high"])
    new_user["tech_level"] = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])

    lifestyle_options = ["Outdoor Sports", "Office Work", "Home", "Travel", "Study"]
    new_user["lifestyle"] = ", ".join(st.multiselect("Lifestyle Preferences", lifestyle_options))

    goals_options = ["Health", "Productivity", "Creativity", "Entertainment", "Learning"]
    new_user["goals"] = ", ".join(st.multiselect("Your Goals", goals_options))

    devices_options = ["iPhone", "Mac", "iPad", "AirPods", "Apple Watch", "Camera"]
    new_user["devices_owned"] = ", ".join(st.multiselect("Devices you own", devices_options))

    if st.button("Create Account"):
        errors = validate_user_input(new_user)
        if errors:
            st.error("❌ Please correct the following:")
            for e in errors:
                st.write(f"- {e}")
        else:
            global users_df
            users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
            st.success("🎉 Account created successfully! Please login.")
            st.session_state["page"] = "login"

def recommendations():
    st.markdown("## 🎉 Welcome to your personalized dashboard!")
    st.markdown("💡 We've picked some products and services just for you based on your profile!")

    user = st.session_state["user"]

    # Προϊόντα
    product_recs = products_df[
        (products_df['category'] == 'product') &
        ((products_df['target_profession'].isin([user["profession"], "All"])) |
         (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(",")))))
    ].head(2)

    # Υπηρεσίες
    service_recs = products_df[
        (products_df['category'] == 'service') &
        ((products_df['target_profession'].isin([user["profession"], "All"])) |
         (products_df['target_interests'].apply(lambda x: any(i in user["interests"] for i in str(x).split(",")))))
    ].head(2)

    if not product_recs.empty:
        st.subheader("🛍️ Recommended Products")
        for _, row in product_recs.iterrows():
            st.markdown(f"**{row['name']}** - €{row['price']}")
            st.markdown(f"[Learn more]({row['url']})")
            if st.button(f"➕ Add {row['name']} to Cart", key=row["id"]):
                st.success(f"✅ {row['name']} added to cart!")

    if not service_recs.empty:
        st.subheader("🛎️ Recommended Services")
        for _, row in service_recs.iterrows():
            st.markdown(f"**{row['name']}** - €{row['price']}")
            st.markdown(f"[Learn more]({row['url']})")
            if st.button(f"➕ Add {row['name']} to Cart", key=f"service_{row['id']}"):
                st.success(f"✅ {row['name']} added to cart!")

    if product_recs.empty and service_recs.empty:
        st.info("No suggestions found for you yet. Update your profile for better recommendations!")

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











