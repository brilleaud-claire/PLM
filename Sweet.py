# Sweet app
import streamlit as st
from streamlit import components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# to create a dashboard
import time
import numpy as np
import plotly.express as px  # interactive charts

# Database
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

from data_yahourt import (
    connection_yahourt,
    creer_yaourt,
    modifier_yaourt,
    chercher_yaourts_par_nom
)

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

# Dashboard
# region test
def Dashboard():
    # read csv from a github repo
    dataset_url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"

    # read csv from a URL
    @st.cache_data
    def get_data() -> pd.DataFrame:
        return pd.read_csv(dataset_url)

    df = get_data()

    # dashboard title
    st.title("Real-Time / Live Data Science Dashboard")

    # top-level filters
    job_filter = st.selectbox("Select the Job", pd.unique(df["job"]))

    # creating a single-element container
    placeholder = st.empty()

    # dataframe filter
    df = df[df["job"] == job_filter]

    # near real-time / live feed simulation
    for seconds in range(200):

        df["age_new"] = df["age"] * np.random.choice(range(1, 5))
        df["balance_new"] = df["balance"] * np.random.choice(range(1, 5))

        # creating KPIs
        avg_age = np.mean(df["age_new"])

        count_married = int(
            df[(df["marital"] == "married")]["marital"].count()
            + np.random.choice(range(1, 30))
        )

        balance = np.mean(df["balance_new"])

        with placeholder.container():

            # create three columns
            kpi1, kpi2, kpi3 = st.columns(3)

            # fill in those three columns with respective metrics or KPIs
            kpi1.metric(
                label="Age ⏳",
                value=round(avg_age),
                delta=round(avg_age) - 10,
            )
            
            kpi2.metric(
                label="Married Count 💍",
                value=int(count_married),
                delta=-10 + count_married,
            )
            
            kpi3.metric(
                label="A/C Balance ＄",
                value=f"$ {round(balance,2)} ",
                delta=-round(balance / count_married) * 100,
            )

            # create two columns for charts
            fig_col1, fig_col2 = st.columns(2)
            with fig_col1:
                st.markdown("### First Chart")
                fig = px.density_heatmap(
                    data_frame=df, y="age_new", x="marital"
                )
                st.write(fig)
                
            with fig_col2:
                st.markdown("### Second Chart")
                fig2 = px.histogram(data_frame=df, x="age_new")
                st.write(fig2)

            st.markdown("### Detailed Data View")
            st.dataframe(df)
            time.sleep(1)  

# endregion

def ajouter_yaourt():
    st.title("New yaourt :")

    # Inputs pour créer un yaourt
    nom = st.text_input("Name of the yaourt")
    version = st.text_input("Version (exemple : v1.0)")
    recette = st.text_input("Recette (ingrédients séparés par des virgules)")
    volume = st.number_input("Volume (en ml)", min_value=0.0)
    level_access = st.number_input("Level Access (1 ou 2)", min_value=1, max_value=2)
    materiaux_emballage = st.text_input("Materials")
    temps_fabrication = st.number_input("Temps de fabrication (in min)", min_value=0.0)
    prix_ingredients = st.number_input("Prix total des ingrédients", min_value=0.0)
    prix_production = st.number_input("Prix de production", min_value=0.0)
    prix_vente = st.number_input("Prix de vente", min_value=0.0)
    date_mise_production = st.date_input("Date de mise en production", value=None)
    date_peremption = st.date_input("Date de péremption", value=None)
    description = st.text_input("Description")
    produit_valide = st.checkbox("le produit est valide")
    marketing_valide = st.checkbox("le marketing est valide")
    employee_id = st.text_input("ID employé")
    projet_id = st.text_input("ID projet")
    date_mise_vente = st.date_input("Date de mise en vente", value=None)

    if st.button("ADD"):
        db = connection_yahourt()
        
        creer_yaourt(db, 
                     nom, 
                     version, 
                     recette, 
                     volume, 
                     level_access, 
                     materiaux_emballage, 
                     temps_fabrication, 
                     prix_ingredients, 
                     prix_production, 
                     prix_vente, 
                     datetime.combine(date_mise_production, datetime.min.time()),
                     datetime.combine(date_peremption, datetime.min.time()), 
                     description, 
                     produit_valide, 
                     marketing_valide, 
                     employee_id, 
                     projet_id,
                     datetime.combine(date_mise_vente, datetime.min.time())
                     )
        st.success(f"Le yaourt '{nom}' a été ajouté avec succès.")


# Search tool and pages names
# region test
# For the search bar
if "search_results" not in st.session_state:
    st.session_state.search_results = [] 

# Pages
PAGES = {
    "Dashboard": Dashboard,
    "Add a product": ajouter_yaourt,
    "Modify a product": "Modifier un yaourt existant.",
    "Search a product": "Recherche dans la base de données.",
}

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
                st.stop()
    else:
        st.sidebar.write("No result found")

    # Select pages
    selected_page = st.sidebar.radio("Or choose a page :", list(PAGES.keys()))
    display_page(selected_page)

        # Log out Button
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# endregion

def display_page(page_name):
    st.header(page_name)
    page_content = PAGES[page_name]
    if callable(page_content):
        page_content()
    else :
        st.write(PAGES[page_name])

# Need to have the log for the other pages
if st.session_state.logged_in:
    Home()
else:
    login_page()