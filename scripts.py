import streamlit as st
import pandas as pd
import os
from datetime import date
import openai

# ======================
# OpenAI API
# ======================
openai.api_key = os.getenv("OPENAI_API_KEY")

# ======================
# LOAD CSVs
# ======================
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/refs/heads/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/refs/heads/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=';', encoding='utf-8')
products_df = pd.read_csv(products_file, sep=';', encoding='utf-8')

# Clean & rename columns
users_df.columns = users_df.columns.str.strip()
users_df.rename(columns={
    users_df.columns[0]: 'username',
    users_df.columns[1]: 'password',
    users_df.columns[2]: 'first_name',
    users_df.columns[3]: 'last_name',
    users_df.columns[4]: 'dob',
    users_df.columns[5]: 'city',
    users_df.columns[6]: 'profession',
    users_df.columns[7]: 'interests',
    users_df.columns[8]: 'budget',
    users_df.columns[9]: 'tech_level',
    users_df.columns[10]: 'lifestyle',
    users_df.columns[11]: 'goals',
    users_df.columns[12]: 'devices_owned'
}, inplace=True)

# ======================
# Streamlit UI
# ======================
st.title("iStorm Apple Store")

menu = ["Login", "Sign Up", "Forgot Password"]
choice = st.sidebar.selectbox("Menu", menu)

# ======================
# SIGN UP
# ======================
if choice == "Sign Up":
    st.subheader("Create a new account")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    email = st.text_input("Email")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input("Date of Birth", min_value=date(1,1,1), max_value=date.today())
    city = st.text_input("City")
    profession = st.text_input("Profession")
    interests = st.text_input("Interests (comma separated)")
    budget = st.selectbox("Budget", ["low", "medium", "high"])
    tech_level = st.selectbox("Tech Level", ["beginner", "intermediate", "advanced"])
    lifestyle = st.text_input("Lifestyle (comma separated)")
    goals = st.text_input("Goals (comma separated)")
    devices_owned = st.text_input("Devices Owned (comma separated)")

    if st.button("Sign Up"):
        if new_username in users_df['username'].values:
            st.warning("Username already exists!")
        elif email in users_df['email'].values if 'email' in users_df.columns else False:
            st.warning("Email already used!")
        else:
            new_row = {
                "username": new_username,
                "password": new_password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "dob": str(dob),
                "city": city,
                "profession": profession,
                "interests": interests,
                "budget": budget,
                "tech_level": tech_level,
                "lifestyle": lifestyle,
                "goals": goals,
                "devices_owned": devices_owned
            }
            users_df = pd.concat([users_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Account created! Please login.")

# ======================
# LOGIN
# ======================
if choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        user_row = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if not user_row.empty:
            st.success(f"Welcome {user_row.iloc[0]['first_name']}!")

            # AI Recommendations sample
            st.subheader("Recommended for you:")
            profession = user_row.iloc[0]['profession']
            interests = user_row.iloc[0]['interests'].split(",")

            recommended = products_df[
                (products_df['target_profession'].str.contains(profession, case=False)) |
                (products_df['target_interests'].apply(lambda x: any(i.lower() in x.lower() for i in interests)))
            ]

            for idx, row in recommended.head(4).iterrows():
                st.write(f"**{row['name']}** ({row['category']}) - ${row['price']}")
                st.write(f"[Go to product]({row['url']})")
                if st.button(f"Add {row['name']} to cart", key=idx):
                    st.success(f"{row['name']} added to cart!")

        else:
            st.error("Username/Password incorrect")

# ======================
# FORGOT PASSWORD
# ======================
if choice == "Forgot Password":
    st.subheader("Recover your password")
    email_input = st.text_input("Enter your registered email")
    if st.button("Recover Password"):
        if 'email' not in users_df.columns:
            st.error("No email information available.")
        else:
            user_row = users_df[users_df['email'] == email_input]
            if not user_row.empty:
                st.info(f"Your username: {user_row.iloc[0]['username']}")
                st.info(f"Your password: {user_row.iloc[0]['password']}")
            else:
                st.error("Email not found")

