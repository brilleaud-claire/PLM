# Sweet app
import streamlit as st
from streamlit import components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Presentation
# region test

st.set_page_config(
    page_title="SWEET YOGURT",
    layout="wide"
)
col1, col2 = st.columns([4, 1])  # Ajustez les proportions si nécessaire
# Title 
with col1:
    st.title(":blue[SWEET YOGURT]")
# Logo
with col2:
    st.image("sweet.png", width=150) 
        
st.subheader("created by Noémie, Claire, Tulipe and Bérénice")
st.markdown("SB A5 -- ESILV")

# endregion

# Login
# region test

VALID_USERS = {
    "admin": "0000",
    "user1": "1234",
    "user2": "5678"
}


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def login_page():
    st.subheader("Connection")

    with st.form("login_form"):
        username = st.text_input("User name")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log in")

        if submit_button:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.success("Connection successful !")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Incorrect username or password.")

# endregion

# Search tool
# region test
# For the search bar
if "search_results" not in st.session_state:
    st.session_state.search_results = [] 

# Pages
PAGES = {
    "Page 1": "C'est un gars qui entre dans un bar.",
    "Page 2": "Il dit 'c'est moi!' ",
    "Page 3": "Et en fait c'était pas lui"}

# to search in the content or title
def search_pages(query):
    query_lower = query.lower()
    results = []
    for page, content in PAGES.items():
        if query_lower in page.lower() or query_lower in content.lower():
            results.append(page)
    return results
# endregion

# Navigation
# region test
def Home():
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    
    # Search
    st.sidebar.write("**Search**")
    query = st.sidebar.text_input("Search in pages : ")
    if query:
        st.session_state.search_results = search_pages(query)
    
    if st.session_state.search_results:
        st.sidebar.write("Results :")
        for result in st.session_state.search_results:
            if st.sidebar.button(f"Go to {result}"):
                st.experimental_set_query_params(page=result)
                display_page(result)

    # Menu de navigation classique
    selected_page = st.sidebar.radio("Or choose a page :", list(PAGES.keys()))
    display_page(selected_page)

        # Bouton de déconnexion
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# endregion

def display_page(page_name):
    st.header(page_name)
    st.write(PAGES[page_name])


# Need to have the log for the other pages
if st.session_state.logged_in:
    Home()
else:
    login_page()