# streamlit_ecommerce_with_key.py
import streamlit as st
import pandas as pd
import openai
import os

# --- Ρύθμιση OpenAI API Key από περιβάλλον ---
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("Please set your OPENAI_API_KEY in environment variables.")

# --- Φόρτωση datasets ---
users_file = "https://raw.githubusercontent.com/dafnipz/iStorm/refs/heads/main/20250903_Users.csv"
products_file = "https://raw.githubusercontent.com/dafnipz/iStorm/refs/heads/main/20250903_ProductList.csv"

users_df = pd.read_csv(users_file, sep=',', encoding='utf-8')
products_df = pd.read_csv(products_file, sep=',', encoding='utf-8')
# --- Session state initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.cart = []

# --- Sidebar: Login / Sign Up ---
st.sidebar.title("Account")
mode = st.sidebar.radio("Choose action", ["Login", "Sign Up"])

def sign_up():
    st.sidebar.subheader("Create a new account")
    new_username = st.sidebar.text_input("Username", key="signup_user")
    new_password = st.sidebar.text_input("Password", type="password", key="signup_pass")
    first_name = st.sidebar.text_input("First Name")
    last_name = st.sidebar.text_input("Last Name")
    dob = st.sidebar.date_input("Date of Birth")
    city = st.sidebar.text_input("City")
    profession = st.sidebar.text_input("Profession")
    interests = st.sidebar.text_input("Interests (comma separated)")
    budget = st.sidebar.selectbox("Budget", ["low","medium","high"])
    tech_level = st.sidebar.selectbox("Tech Level", ["beginner","intermediate","advanced"])
    lifestyle = st.sidebar.text_input("Lifestyle")
    goals = st.sidebar.text_input("Goals")
    devices_owned = st.sidebar.text_input("Devices Owned (comma separated)")

    if st.sidebar.button("Sign Up"):
        if new_username in users_df['username'].values:
            st.sidebar.error("Username already exists!")
        else:
            new_user = {
                "username": new_username,
                "password": new_password,
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "city": city,
                "profession": profession,
                "interests": interests,
                "budget": budget,
                "tech_level": tech_level,
                "lifestyle": lifestyle,
                "goals": goals,
                "devices_owned": devices_owned
            }
            users_df.loc[len(users_df)] = new_user
            users_df.to_csv(users_file, index=False, encoding="utf-8")
            st.sidebar.success("Account created! You can now login.")

def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user_row = users_df[(users_df['username']==username) & (users_df['password']==password)]
        if not user_row.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {user_row.iloc[0]['first_name']}!")
        else:
            st.error("Invalid credentials")

if mode == "Sign Up":
    sign_up()
elif mode == "Login":
    login()

# --- Main app ---
if st.session_state.logged_in:
    user_row = users_df[users_df['username'] == st.session_state.username].iloc[0]

    # Profile display
    st.markdown(f"### Welcome {user_row['first_name']} {user_row['last_name']}!")
    st.write({
        "DOB": user_row['dob'],
        "City": user_row['city'],
        "Profession": user_row['profession'],
        "Interests": user_row['interests'],
        "Budget": user_row['budget'],
        "Tech Level": user_row['tech_level'],
        "Lifestyle": user_row['lifestyle'],
        "Goals": user_row['goals'],
        "Devices Owned": user_row['devices_owned']
    })

    # AI Recommendations
    st.subheader("Recommended Products & Services")
    prompt = f"""
    Given the user profile:
    Name: {user_row['first_name']} {user_row['last_name']}
    Profession: {user_row['profession']}
    Interests: {user_row['interests']}
    Budget: {user_row['budget']}
    Devices Owned: {user_row['devices_owned']}
    Suggest 2 products and 2 services from the following list:
    {products_df[['name','category','target_profession','target_interests','url']].to_dict(orient='records')}
    Return the suggestions with name, category, url.
    """

    if st.button("Get Recommendations"):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role":"user","content":prompt}],
                max_tokens=300
            )
            suggestions_text = response['choices'][0]['message']['content']
            st.markdown(suggestions_text)
        except Exception as e:
            st.error(f"OpenAI API Error: {e}")

        # --- Display products as colored cards with Add to Cart ---
        st.subheader("Your Recommendations")
        for _, row in products_df.iterrows():
            with st.container():
                st.markdown(f"""
                    <div style="border:2px solid #4CAF50; padding:10px; border-radius:10px; margin-bottom:10px; background-color:#f0f8ff;">
                        <h4 style="color:#2E8B57;">{row['name']} ({row['category']})</h4>
                        <p>Target Profession: {row['target_profession']}</p>
                        <p>Target Interests: {row['target_interests']}</p>
                        <p>Price: €{row['price']}</p>
                        <a href="{row['url']}" target="_blank"><button style="background-color:#4CAF50; color:white; padding:5px 10px; border:none; border-radius:5px;">View Product</button></a>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Add {row['name']} to Cart"):
                    st.session_state.cart.append(row['name'])
                    st.success(f"Added {row['name']} to cart!")

    # --- Display Cart ---
    st.subheader("Your Cart")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.write(f"🛒 {item}")
    else:
        st.write("Your cart is empty.")


