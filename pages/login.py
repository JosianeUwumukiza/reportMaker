import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="./.env")  # Load variables from .env file
APP_PASSWORD = os.getenv("APP_PASSWORD")

# --- Load custom CSS ---
def local_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("./style.css")

st.markdown("<div class='login-page'>", unsafe_allow_html=True)

# Predefined username and password
USERNAME = "admin"
PASSWORD = APP_PASSWORD

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("You are logged in! Please navigate to the Home page.")
        else:
            st.error("Invalid username or password")

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

check_authentication()
login()
st.markdown("</div>", unsafe_allow_html=True)
