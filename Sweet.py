# Sweet app
import streamlit as st
from streamlit import components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(
    page_title="SWEET YOGURT",
    layout="wide"
)

# Presentation
col1, col2 = st.columns([4, 1])  # Ajustez les proportions si nécessaire

# Title 
with col1:
    st.title(":blue[SWEET YOGURT]")

# Logo
with col2:
    st.image("sweet.png", width=150) 
        
st.subheader("created by Noémie, Claire, Tulipe and Bérénice")
st.markdown("SB A5 -- ESILV")

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
    st.subheader("Connexion")

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("Se connecter")

        if submit_button:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.success("Connexion réussie !")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

# endregion

def Home():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}!")
    st.sidebar.subheader("Navigation")
    
    # Menu de navigation
    page = st.sidebar.radio("Aller à", ["Page 1", "Page 2", "Déconnexion"])

    if page == "Page 1":
        st.header("Page 1")
        st.write("Contenu de la première page.")
    elif page == "Page 2":
        st.header("Page 2")
        st.write("Contenu de la deuxième page.")
    elif page == "Déconnexion":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Vous êtes déconnecté.")

# Afficher la page appropriée
if st.session_state.logged_in:
    Home()
else:
    login_page()