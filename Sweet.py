# importation
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
from hashlib import sha256
from bson import ObjectId
import gridfs
import io

from data_yahourt import (
    connection_yahourt,
    creer_yaourt,
    modifier_yaourt,
)
from data_employe import (connection_employe,
                          creer_employe,
                          modifier_employe,
                          chercher_employe_par_id,
                          chercher_employe_par_job_title,
                          chercher_employe_par_level_access,
                          modifier_id_employe,
                          chercher_employes_par_modification_date)

from data_yahourt import (
    chercher_yaourt_par_id,
    chercher_yaourts_par_date_production,
    chercher_yaourts_par_date_peremption,
    chercher_yaourts_par_date_vente,
    chercher_yaourts_par_nom,
    chercher_yaourts_par_validation_produit,
    chercher_yaourts_par_validation_marketing,
    chercher_yaourts_par_derniere_modification_date,
    chercher_yaourts_par_employee_id_modification
)
from data_project import (
    connection_projet,
    creer_projet,
    modifier_projet,
    chercher_projet_par_id,
    chercher_projets_par_date_debut,
    chercher_projets_par_date_fin,
    chercher_projets_par_budget,
    chercher_projets_par_employee_id_modification,
    chercher_projets_par_recette,
    inserer_pdf_avec_gridfs,
    recuperer_pdf_avec_gridfs
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def login_page(db):
    st.subheader("Connection")

    with st.form("login_form"):
        username = st.text_input("ID")
        password = st.text_input("Password", type="password")
        password = password.strip()
        submit_button = st.form_submit_button("Log in")

        if submit_button:
            employe = db.employes.find_one({"_id": username})
            if employe:
                if employe['password'] == sha256(password.encode()).hexdigest():
                    st.success("Successful connection !")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")

# endregion

# Employés
# region test
def modifier_employe_page(db):
    employee_id = st.session_state.username    
    employe = db.employes.find_one({"_id": employee_id})
    
    if employe:
        st.subheader("Current informations")
        for key, value in employe.items():
            if key != "_id" and key != "password": 
                st.write(f"{key}: {value}")
        
        with st.form("modifier_form"):
            new_level_access = st.number_input("New access level", min_value=1, value=employe['level_access'])
            new_job_title = st.text_input("New job title", value=employe['job_title'])
            new_password = st.text_input("New password", type="password")
            
            submit_button = st.form_submit_button("Update")
            
            if submit_button:
                updates = {}
                if new_level_access != employe['level_access']:
                    updates["level_access"] = new_level_access
                if new_job_title != employe['job_title']:
                    updates["job_title"] = new_job_title
                if new_password:
                    updates["password"] = sha256(new_password.encode()).hexdigest()
                
                # Update database
                if updates:
                    try:
                        modifier_employe(db, employee_id, updates)
                        st.success(f"Update done !")
                    except ValueError as e:
                        st.error(str(e))
                else:
                    st.warning("No update done")
    else:
        st.error("User no found")

def creer_employe_page(db):
    if st.session_state.username == "admin":
        
        with st.form("ajouter_employe_form"):

            employee_id = st.text_input("ID")
            level_access = st.number_input("Level of access", min_value=1, max_value=5, value=1)
            job_title = st.text_input("Job title")
            password = st.text_input("Password", type="password")
            
            submit_button = st.form_submit_button("Create")
            
            if submit_button:
                employe_exist = db.employes.find_one({"_id": employee_id})
                if employe_exist:
                    st.error(f"{employee_id} already exist.")
                else:
                    hashed_password = sha256(password.encode()).hexdigest()
                    
                    new_employee_data = {
                        "_id": employee_id,
                        "level_access": level_access,
                        "job_title": job_title,
                        "password": hashed_password
                    }

                    try:
                        creer_employe(db, employee_id, level_access, job_title, hashed_password)
                        st.success(f"Success ! ")
                    except Exception as e:
                        st.error(f"Error : {str(e)}")
    else:
        st.error("You must be an administrator to access this page.")
        st.query_params = {"page": "Home"}
        st.rerun()

def rechercher_employe_page(db):
    st.write("Select a search criterion and enter the corresponding value.")

    # Étape 1 : Sélectionner le critère de recherche
    critere = st.selectbox(
        "Search criterion",
        ["-- CHOOSE --", "ID", "Job title", "Level access", "Modification date"]
    )

    if critere == "ID":
        employe_id = st.text_input("Enter ID")
        if st.button("Search"):
            employe = chercher_employe_par_id(db, employe_id)
            if employe:
                st.write("**Result :**")
                st.json(employe)
            else:
                st.error("No employees found.")
    
    elif critere == "Job title":
        job_title = st.text_input("Enter the job title")
        if st.button("Search"):
            employes = chercher_employe_par_job_title(db, job_title)
            if employes:
                st.write(f"**{len(employes)} employee(s) found :**")
                st.dataframe(pd.DataFrame(employes))
            else:
                st.error("No employees found.")
    
    elif critere == "Level access":
        level_access = st.number_input("Enter the level access", min_value=1, step=1)
        if st.button("Search"):
            employes = chercher_employe_par_level_access(db, level_access)
            if employes:
                st.write(f"**{len(employes)} employee(s) found :**")
                st.dataframe(pd.DataFrame(employes))
            else:
                st.error("No employees found.")
    
    elif critere == "Modification date":
        date_modification = st.date_input("Enter modification date (AAAA-MM-JJ)")
        if st.button("Search"):
            employes = chercher_employes_par_modification_date(db, date_modification.strftime("%Y-%m-%d"))
            if employes:
                st.write(f"**{len(employes)} employee(s) modified since this date :**")
                st.dataframe(pd.DataFrame(employes))
            else:
                st.error("No employees found.")
    else:
        st.write("Select a criteron.")
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

# Yaourts
# region test
def ajouter_yaourt():
    nom = st.text_input("Name")
    version = st.text_input("Version (ex: v1.0)")
    recette = st.text_input("Recipe (ingredients separated by commas)")
    
    volume = st.number_input("Volume (in ml)", min_value=0.0)
    if volume <= 0:
        st.error("volume must be > 0 .")
    
    level_access = st.number_input("Access Level (1 or 2)", min_value=1, max_value=2)
    materiaux_emballage = st.text_input("Packaging materials")
    temps_fabrication = st.number_input("Production time (in min)", min_value=0.0)
    prix_ingredients = st.number_input("Price of ingredients (in euros)", min_value=0.0)
    prix_production = st.number_input("Production price (in euros)", min_value=0.0)
    prix_vente = st.number_input("Selling price (in euros)", min_value=0.0)
    
    date_mise_production = st.date_input("Production start date (AAAA/MM/DD)")
    date_peremption = st.date_input("Expiry date (AAAA/MM/DD)")
    description = st.text_input("Description")
    produit_valide = st.checkbox("Validated product")
    marketing_valide = st.checkbox("Validated marketing")
    
    employee_id = st.session_state.username
    projet_id = st.text_input("ID Projet")
    date_mise_vente = st.date_input("Date of sale", value=None)

    if st.button("Add"):
        if volume > 0 and prix_vente > 0:
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
            st.success(f"The yoghurt '{nom}' has been added.")
        else:
            st.error("Please check that all fields are filled.")

def modifier_yaourt_page():
    db = connection_yahourt()
    employee_id = st.session_state.username

    id_yaourt = st.text_input("Entrez l'ID du yaourt à modifier :")

    if id_yaourt:
        try:
            yaourt = db.yaourts.find_one({"_id": ObjectId(id_yaourt)})
        except Exception as e:
            st.error(f"Erreur lors de la recherche du yaourt : {str(e)}")
            return
        
        if yaourt:
            st.subheader("Current information")
            for key, value in yaourt.items():
                if key != "_id":
                    st.write(f"**{key}:** {value}")

            with st.form("modifier_form"):
                nouveau_nom = st.text_input("New name", value=yaourt.get('nom', ''))
                nouveau_type = st.text_input("New type", value=yaourt.get('type', ''))
                nouveau_prix_vente = st.number_input("New selling price ", min_value=0.0, value=yaourt.get('prix_vente', 0.0))
                nouveau_prix_ingredients = st.number_input("New ingredient prices", min_value=0.0, value=yaourt.get('prix_ingredients', 0.0))
                nouveau_prix_production = st.number_input("New production price", min_value=0.0, value=yaourt.get('prix_production', 0.0))
                nouvelle_description = st.text_area("New description", value=yaourt.get('description', ''))
                nouvelle_validation_produit = st.checkbox("Validation product", value=yaourt.get('validation.produit', False))
                nouvelle_validation_marketing = st.checkbox("Validation marketing", value=yaourt.get('validation.marketing', False))

                submit_button = st.form_submit_button("Update")

                if submit_button:
                    updates = {}

                    if nouveau_nom != yaourt.get('nom', ''):
                        updates["nom"] = nouveau_nom
                    if nouveau_type != yaourt.get('type', ''):
                        updates["type"] = nouveau_type
                    if nouveau_prix_vente != yaourt.get('prix_vente', 0.0):
                        updates["prix_vente"] = nouveau_prix_vente
                    if nouveau_prix_ingredients != yaourt.get('prix_ingredients', 0.0):
                        updates["prix_ingredients"] = nouveau_prix_ingredients
                    if nouveau_prix_production != yaourt.get('prix_production', 0.0):
                        updates["prix_production"] = nouveau_prix_production
                    if nouvelle_description != yaourt.get('description', ''):
                        updates["description"] = nouvelle_description
                    if nouvelle_validation_produit != yaourt.get('validation.produit', False):
                        updates["validation.produit"] = nouvelle_validation_produit
                    if nouvelle_validation_marketing != yaourt.get('validation.marketing', False):
                        updates["validation.marketing"] = nouvelle_validation_marketing

                    if updates:
                        try:
                            modifier_yaourt(
                                db=db,
                                yaourt_id=ObjectId(id_yaourt),
                                updates=updates,
                                employee_id=employee_id
                            )
                            st.success(f"Update successful!")
                        except Exception as e:
                            st.error(f"Error : {str(e)}")
                    else:
                        st.warning("No changes made.")
        else:
            st.error("Yoghurt not found with this ID.")

def rechercher_yaourt_page():
    db = connection_yahourt()
        
    critere = st.selectbox(
        "Search criterion",
        ["-- CHOOSE --", "ID", "Production Date", "Expiry Date", "Sale Date",
         "Name", "Product Validation", "Marketing Validation", "Last Modification", "Employee who modified"]
    )

    if critere == "ID":
        yogurt_id = st.text_input("Enter the yogurt ID:")
        
        if st.button("Search"):
            yogurt = chercher_yaourt_par_id(db, yogurt_id)
            if yogurt:
                st.write("**Result:**")
                st.json(yogurt)
            else:
                st.error("No yogurt found.")
    
    elif critere == "Production Date":
        production_date = st.date_input("Enter production date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            yogurts = chercher_yaourts_par_date_production(db, production_date)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")

    elif critere == "Expiry Date":
        expiry_date = st.date_input("Enter expiry date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            yogurts = chercher_yaourts_par_date_peremption(db, expiry_date)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
    
    elif critere == "Sale Date":
        sale_date = st.date_input("Enter sale date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            yogurts = chercher_yaourts_par_date_vente(db, sale_date)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
            
    elif critere == "Name":
        nom = st.text_input("Enter the yogurt name:")
        if st.button("Search"):
            yogurts = chercher_yaourts_par_nom(db, nom)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")

    
    elif critere == "Product Validation":
        product_valid = st.selectbox("Product validation", ["Yes", "No"])
        product_valid = True if product_valid == "Yes" else False
        if st.button("Search"):
            yogurts = chercher_yaourts_par_validation_produit(db, product_valid)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
    
    elif critere == "Marketing Validation":
        marketing_valid = st.selectbox("Marketing validation", ["Yes", "No"])
        marketing_valid = True if marketing_valid == "Yes" else False
        if st.button("Search"):
            yogurts = chercher_yaourts_par_validation_marketing(db, marketing_valid)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
    
    elif critere == "Last Modification":
        modification_date = st.date_input("Enter last modification date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        if st.button("Search"):
            yogurts = chercher_yaourts_par_derniere_modification_date(db, modification_date.strftime("%Y-%m-%d"))
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) modified since this date:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
    
    elif critere == "Employee who modified":
        employee_id = st.text_input("Enter the employee ID who modified:")
        if st.button("Search"):
            yogurts = chercher_yaourts_par_employee_id_modification(db, employee_id)
            if yogurts:
                st.write(f"**{len(yogurts)} yogurt(s) found:**")
                st.dataframe(pd.DataFrame(yogurts))
            else:
                st.error("No yogurt found.")
    else:
        st.write("Please select a criterion.")
# endregion

# EBOM
# region test
# Utilisation dans l'application Streamlit
def pdf_id() :
    db = connection_projet()
    pdf_id = st.text_input("Entrez l'ID du PDF à télécharger :")
    if pdf_id:
        telecharger_pdf_avec_streamlit(db, pdf_id)
    
def telecharger_pdf_avec_streamlit(db, pdf_id):
    db = connection_projet()

    fs = gridfs.GridFS(db)
    try:
        object_id = ObjectId(pdf_id)
        pdf_data = fs.get(object_id)
        
        # Préparer le fichier en mémoire
        pdf_bytes = io.BytesIO(pdf_data.read())
 
        # Créer un lien de téléchargement Streamlit
        st.download_button(
            label="Télécharger le PDF",
            data=pdf_bytes,
            file_name=pdf_data.filename,
            mime="application/pdf"
        )
    except gridfs.NoFile:
        st.error("Fichier introuvable dans GridFS.")

# endregion

# Search tool and pages names
# region test
# For the search bar
if "search_results" not in st.session_state:
    st.session_state.search_results = [] 

db = connection_employe()

# Pages
PAGES = {
    "Modification of information" : lambda: modifier_employe_page(db),
    "Add a new employe" : lambda: creer_employe_page(db),
    "Search an employe" : lambda: rechercher_employe_page(db),
    "Dashboard": Dashboard,
    "Add a product": ajouter_yaourt,
    "Modify a product": modifier_yaourt_page,
    "Search a product": rechercher_yaourt_page,
    "EBOM à telecharger" : lambda : pdf_id()
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
    
    page_container = st.empty()
    
    st.sidebar.write("**Search**")
    query = st.sidebar.text_input("Search in pages : ")
    if query:
        st.session_state.search_results = search_pages(query)
    
    if st.session_state.search_results:
        st.sidebar.write("Results :")
        for result in st.session_state.search_results:
            if st.sidebar.button(f"Go to {result}"):
                st.session_state.selected_page = result
                page_container.empty()
                page_container.write(f"Loading {result}...")
                display_page(result, container=page_container)
                return
    else:
        st.sidebar.write("No result found")
    
    selected_page = st.sidebar.radio("Or choose a page :", list(PAGES.keys()))
    if st.session_state.get("selected_page") != selected_page:
        st.session_state.selected_page = selected_page
        page_container.empty() 
        
    display_page(selected_page, container=page_container)

    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.selected_page = None  
        st.rerun()        
# endregion

def display_page(page_name, container=None):    
    if page_name not in PAGES:
        st.error(f"Page '{page_name}' non trouvée.")
        return
    if container is None:
        container = st
    
    container.empty()
    container.header(page_name)
    page_content = PAGES[page_name]
    
    if callable(page_content):
        page_content()
    else:
        container.write(page_content)

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    db = connection_employe()

    if st.session_state.logged_in:
        with st.sidebar:
            st.title("Menu")
        Home()
    else:
        login_page(db)
        pass

if __name__ == "__main__":
    main()