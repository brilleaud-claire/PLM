# importation
import streamlit as st
from streamlit import components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import win32com.client 
import os
import tempfile

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
    modifier_yaourt
    )
from data_employe import (connection_employe,
                          creer_employe,
                          modifier_employe,
                          chercher_employe_par_id,
                          chercher_employe_par_job_title,
                          chercher_employe_par_level_access,
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
    recuperer_pdf_avec_gridfs,
    inserer_fichier_solidworks,
)
from data_historique import (
    connection_historique,
    creer_historique_modification,
    modifier_historique,
    chercher_historique_par_id,
    chercher_historique_par_document_id,
    chercher_historique_par_date_modification,
    chercher_historique_par_employee_id,
)
from cost_opti import(
    calculer_marge,
    ameliorer_couts
)

# Presentation
# region test

st.set_page_config(
    page_title="SWEET YOGURT",
    layout="wide"
)
col1, col2 = st.columns([4, 1])
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
                    level_access = employe.get("level_access", 1)
                    st.session_state.level_access = level_access
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")

# endregion

# Employés
# region test
def modifier_employe_page():
    db = connection_employe()

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

def creer_employe_page():
    db = connection_employe()
    if st.session_state.get("level_access", 0) >= 2:
        
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

def rechercher_employe_page():
    db = connection_employe()
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
        all_employe = list(db.employes.find())
        st.dataframe(pd.DataFrame(all_employe))
# endregion

# Dashboard
# region test
def dashboard_page():
    db = connection_yahourt()
        
    projects = list(db.projets.find({}, {"_id": 1, "nom": 1}))  
    project_options = [p["nom"] for p in projects]  
    selected_project_name = st.selectbox("Select a project:", ["-- CHOOSE --"] + project_options)
    
    if selected_project_name != "-- CHOOSE --":
        
        selected_project = next(p for p in projects if p["nom"] == selected_project_name)
        selected_project_id = selected_project["_id"]
        
        products = list(db.yaourts.find({"projet_id": selected_project_id}))
        
        if not products:
            st.warning("No products found for this project.")
            return
        
        df = pd.DataFrame(products)
        
        st.header("Summary")
        total_products = len(df)
        avg_margin = df["marge"].mean()
        max_margin = df["marge"].max()
        min_margin = df["marge"].min()
        total_cost = df["prix_ingredients"].sum() + df["prix_production"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Products", total_products)
        col2.metric("Average Margin (€)", round(avg_margin, 2))
        col3.metric("Max Margin (€)", round(max_margin, 2))
        col4.metric("Total Cost (€)", round(total_cost, 2))
        
        st.header("Visualizations")
        
        if "date_mise_production" in df.columns:
            df["date_mise_production"] = pd.to_datetime(df["date_mise_production"])
            fig_prod_dates = px.histogram(
                df, 
                x="date_mise_production", 
                title="Distribution of Production Dates",
                labels={"date_mise_production": "Production Date"},
                nbins=10
            )
            st.plotly_chart(fig_prod_dates)
        
        if {"nom", "marge"}.issubset(df.columns):
            fig_marges = px.bar(
                df, 
                x="nom", 
                y="marge", 
                title="Margins by Product",
                labels={"nom": "Product Name", "marge": "Margin (€)"},
                color="marge",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_marges)
        
        if {"nom", "prix_ingredients", "prix_production"}.issubset(df.columns):
            fig_costs = px.bar(
                df, 
                x="nom", 
                y=["prix_ingredients", "prix_production"], 
                title="Comparison of Costs (Ingredients vs Production)",
                labels={"value": "Cost (€)", "nom": "Product Name"},
                barmode="group"
            )
            st.plotly_chart(fig_costs)
        
        st.header("Data Table")
        st.dataframe(df)
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
    projet_id = st.text_input("Product ID")
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
            yaourt = db.yaourts.find_one({"_id": id_yaourt})
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
                nouvelle_version = st.text_input("New version", value=yaourt.get('version', ''))
                nouveau_projet_ID = st.text_input("New project ID", value=yaourt.get('projet_id', ''))
                nouvelle_recette = st.text_area("New recipe", value=yaourt.get('recette', ''))
                nouveau_prix_vente = st.number_input("New selling price", min_value=0.0, value=yaourt.get('prix_vente', 0.0))
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
                    if nouvelle_version != yaourt.get('version', ''):
                        updates["version"] = nouvelle_version
                    if nouveau_projet_ID != yaourt.get('projet_id', ''):
                        updates["projet_id"] = nouveau_projet_ID
                    if nouvelle_recette != yaourt.get('recette', ''):
                        updates["recette"] = nouvelle_recette
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

                    # Update database
                    if updates:
                        try:
                            modifier_yaourt(db, id_yaourt, updates, employee_id)
                            st.success(f"Update done !")
                            
                            modification_date = datetime.utcnow()
                            creer_historique_modification(
                                db=db,
                                type_document="yaourt",
                                document_id=id_yaourt,
                                ancienne_version=yaourt,
                                nouvelle_version={**yaourt, **updates},
                                modification_date=modification_date,
                                employee_id=employee_id
                            )
                            
                            st.success("Historique enregistré avec succès.")
                            
                        except ValueError as e:
                            st.error(str(e))
                    else:
                        st.warning("No update done")
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
            yogurt = chercher_yaourt_par_id(yogurt_id)
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
        all_yogurts = list(db.yaourts.find())
        st.dataframe(pd.DataFrame(all_yogurts))
# endregion

# Projet
# region test
def creer_projet_page():

    nom = st.text_input("Project Name")
    version = st.text_input("Version (e.g. v1.0)")

    level_access = st.number_input("Access Level (1 or 2)", min_value=1, max_value=2)

    date_debut = st.date_input("Project Start Date (YYYY/MM/DD)")
    date_fin = st.date_input("Project End Date (YYYY/MM/DD)")
    
    budget = st.number_input("Budget (in euros)", min_value=0.0)
    recette = st.number_input("Revenue (in euros)", min_value=0.0)
    
    description = st.text_area("Project Description")
    
    employee_id = st.session_state.username 
    projet_id = st.text_input("Project ID")

    if projet_id and len(projet_id) < 5:
        st.warning("Project ID should have at least 5 characters.")

    if st.button("Add Project"):
        if nom and version and projet_id:
            db = connection_projet()
            creer_projet(
                db, 
                projet_id, 
                nom, 
                version, 
                level_access, 
                datetime.combine(date_debut, datetime.min.time()), 
                datetime.combine(date_fin, datetime.min.time()),
                budget, 
                recette, 
                description, 
                employee_id
            )
            st.success(f"The project '{nom}' has been successfully added.")
        else:
            st.error("Please fill in all required fields.")

def modifier_projet_page():
    projet_id = st.text_input("Enter the Project ID")

    if projet_id:
        db = connection_projet()
        projet = db.projets.find_one({"_id": projet_id})

        if projet:
            st.write("Current Project Information:")
            st.json(projet)

            nom = st.text_input("Project Name", value=projet.get("nom", ""))
            version = st.text_input("Version (e.g., v1.0)", value=projet.get("version", ""))
            level_access = st.number_input("Access Level (1 or 2)", min_value=1, max_value=2, value=projet.get("level_access", 1))

            date_debut = st.date_input("Project Start Date (YYYY/MM/DD)", value=projet.get("date_debut", datetime.utcnow()).date()if isinstance(projet.get("date_debut"), datetime) else datetime.utcnow().date())
            date_fin = st.date_input("Project End Date (YYYY/MM/DD)", value=projet.get("date_fin", datetime.utcnow()).date()if isinstance(projet.get("date_debut"), datetime) else datetime.utcnow().date())

            budget = st.number_input("Budget (in euros)", min_value=0.0, value=float(projet.get("budget", 0.0)))
            recette = st.number_input("Revenue (in euros)", min_value=0.0, value=float(projet.get("recette", 0.0)))

            description = st.text_area("Project Description", value=projet.get("description", ""))

            employee_id = st.session_state.username 
            
            if st.button("Update Project"):
                updates = {}
                
                if nom:
                    updates["nom"] = nom
                if version:
                    updates["version"] = version
                if level_access:
                    updates["level_access"] = level_access
                if date_debut:
                    updates["date_debut"] = datetime.combine(date_debut, datetime.min.time())
                if date_fin:
                    updates["date_fin"] = datetime.combine(date_fin, datetime.min.time())
                if budget:
                    updates["budget"] = budget
                if recette:
                    updates["recette"] = recette
                if description:
                    updates["description"] = description

                if updates:
                    try:
                        modifier_projet(db, projet_id, updates, employee_id)
                        
                        modification_date = datetime.utcnow()
                        creer_historique_modification(
                            db=db,
                            type_document="projet",
                            document_id=projet_id,
                            ancienne_version=projet,
                            nouvelle_version={**projet, **updates},
                            modification_date=modification_date,
                            employee_id=employee_id
                        )
                        st.success("Project successfully updated.")
                    except ValueError as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("No changes were made.")
        else:
            st.error("Project not found. Please check the project ID.")

def rechercher_projet_page():
    db = connection_projet()
    
    critere = st.selectbox(
        "Search criterion",
        ["-- CHOOSE --", "ID", "Start Date", "End Date", "Budget", "Revenue", 
         "Employee who modified"]
    )

    if critere == "ID":
        projet_id = st.text_input("Enter the project ID:")
        
        if st.button("Search"):
            projets = chercher_projet_par_id(db, projet_id)
            if projets:
                st.write("**Result:**")
                st.json(projets)
            else:
                st.error("No project found.")
    
    elif critere == "Start Date":
        start_date = st.date_input("Enter start date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            projets = chercher_projets_par_date_debut(db, start_date)
            if projets:
                st.write(f"**{len(projets)} project(s) found:**")
                st.json(projets)
            else:
                st.error("No project found.")

    elif critere == "End Date":
        end_date = st.date_input("Enter end date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            projets = chercher_projets_par_date_fin(db, end_date)
            if projets:
                st.write(f"**{len(projets)} project(s) found:**")
                st.json(projets)
            else:
                st.error("No project found.")
    
    elif critere == "Budget":
        budget_min = st.number_input("Enter minimum budget", min_value=0.0, value=0.0)
        budget_max = st.number_input("Enter maximum budget", min_value=0.0, value=1000000.0)
        
        if st.button("Search"):
            projets = chercher_projets_par_budget(db, budget_min, budget_max)
            if projets:
                st.write(f"**{len(projets)} project(s) found:**")
                st.json(projets)
            else:
                st.error("No project found.")
    
    elif critere == "Revenue":
        revenue_min = st.number_input("Enter minimum revenue", min_value=0.0, value=0.0)
        revenue_max = st.number_input("Enter maximum revenue", min_value=0.0, value=1000000.0)
        
        if st.button("Search"):
            projets = chercher_projets_par_recette(db, revenue_min, revenue_max)
            if projets:
                st.write(f"**{len(projets)} project(s) found:**")
                st.json(projets)
            else:
                st.error("No project found.")
    
    elif critere == "Employee who modified":
        employee_id = st.text_input("Enter the employee ID who modified:")
        
        if st.button("Search"):
            projets = chercher_projets_par_employee_id_modification(db, employee_id)
            if projets:
                st.write(f"**{len(projets)} project(s) found:**")
                st.json(projets)
            else:
                st.error("No project found.")
    
    else:
        all_projects = list(db.projets.find())
        st.json(all_projects)

def rechercher_historique_page():
    db = connection_historique()
        
    critere = st.selectbox(
        "Search criterion",
        ["-- CHOOSE --", "ID", "Document ID", "Modification Date", "Employee ID"]
    )

    if critere == "ID":
        historique_id = st.text_input("Enter the history ID (ObjectId):")
        
        if st.button("Search"):
            historique = chercher_historique_par_id(db, historique_id)
            if historique:
                st.write("**Result:**")
                st.json(historique)
            else:
                st.error("No history found.")
    
    elif critere == "Document ID":
        document_id = st.text_input("Enter the document ID (e.g., yogurt ID):")
        
        if st.button("Search"):
            historiques = chercher_historique_par_document_id(db, document_id)
            if historiques:
                st.write(f"**{len(historiques)} history record(s) found:**")
                st.dataframe(pd.DataFrame(historiques))
            else:
                st.error("No history found.")
    
    elif critere == "Modification Date":
        modification_date = st.date_input("Enter the modification date (YYYY-MM-DD)", min_value=datetime(1900, 1, 1))
        
        if st.button("Search"):
            historiques = chercher_historique_par_date_modification(db, modification_date.strftime("%Y-%m-%d"))
            if historiques:
                st.write(f"**{len(historiques)} history record(s) found:**")
                st.dataframe(pd.DataFrame(historiques))
            else:
                st.error("No history found.")
    
    elif critere == "Employee ID":
        employee_id = st.text_input("Enter the employee ID who modified:")
        
        if st.button("Search"):
            historiques = chercher_historique_par_employee_id(db, employee_id)
            if historiques:
                st.write(f"**{len(historiques)} history record(s) found:**")
                st.dataframe(pd.DataFrame(historiques))
            else:
                st.error("No history found.")
    else:
        all_histo = list(db.historique.find())
        st.dataframe(pd.DataFrame(all_histo))
# endregion

# Présentation projets et produits
# region test
def afficher_projets_et_produits():
    db = connection_projet()
    projets = list(db.projets.find())
    
    if not projets:
        st.warning("Aucun projet trouvé.")
        return
    
    st.header(f"Liste des Projets ({len(projets)})")
    
    for projet in projets:
        st.subheader(f"Projet : {projet['nom']} (ID : {projet['_id']})")
        st.image("yaourt_boire.png", width=150)
        st.write(f"Version : {projet.get('version', 'N/A')}")
        st.write(f"Description : {projet.get('description', 'Pas de description')}")
        st.write(f"Budget : {projet.get('budget', 0.0)} €")
        
        yaourts = list(connection_yahourt().yaourts.find({"projet_id": projet["_id"]}))
        st.write(f"Nombre de produits : {len(yaourts)}")
        
        if yaourts:
            for yaourt in yaourts:
                st.markdown(f"- **{yaourt['nom']}** (ID : {yaourt['_id']})")
        else:
            st.write("Aucun produit associé à ce projet.")
# endregion

# Opti coûts
# region test
def cost_price_simulation_page():

    recette = st.number_input("Enter Revenue (in euros):", min_value=0.0, value=1000.0)
    cout_total = st.number_input("Enter Total Cost (in euros):", min_value=0.0, value=500.0)

    if st.button("Calculate Margin"):
        marge = calculer_marge(recette, cout_total)
        st.write(f"**Margin:** {marge:.2f} euros")

def ameliorer_couts_et_marges_yaourt_page():
    db = connection_yahourt()

    yaourts = db.yaourts.find()
    yaourt_list = [yaourt['nom'] for yaourt in yaourts]

    selected_yaourt = st.selectbox("Select a yogurt to improve costs", yaourt_list)

    if selected_yaourt:
        yaourt_details = db.yaourts.find_one({"nom": selected_yaourt})

        if yaourt_details:
            st.write(f"### Selected Yogurt: {selected_yaourt}")
            st.json(yaourt_details)

            prix_ingredients = yaourt_details.get("prix_ingredients", 0.0)
            prix_production = yaourt_details.get("prix_production", 0.0)
            prix_vente = yaourt_details.get("prix_vente", 0.0)
            marge_actuelle = yaourt_details.get("marge", 0.0)

            st.write(f"- **Price of ingredients:** {prix_ingredients} EUR")
            st.write(f"- **Price of production:** {prix_production} EUR")
            st.write(f"- **Selling price:** {prix_vente} EUR")
            st.write(f"- **Current margin:** {marge_actuelle} EUR")

            reduction_ingredients = st.number_input("Reduction on ingredients (%)", min_value=0.0, max_value=100.0, value=0.0)
            reduction_production = st.number_input("Reduction on production (%)", min_value=0.0, max_value=100.0, value=0.0)
            nouveau_prix_vente = st.number_input("New desired selling price (EUR)", min_value=0.0, value=prix_vente)

            if st.button("Calculate optimized costs and margins"):
                
                prix_ingredients_optimise, prix_production_optimise, cout_total_optimise = ameliorer_couts(
                    prix_ingredients, prix_production, reduction_ingredients, reduction_production
                )

                marge_optimisee = calculer_marge(nouveau_prix_vente, cout_total_optimise)

                st.write("### Optimized Results:")
                st.write(f"- **Optimized price of ingredients:** {prix_ingredients_optimise:.2f} EUR")
                st.write(f"- **Optimized price of production:** {prix_production_optimise:.2f} EUR")
                st.write(f"- **Optimized total cost:** {cout_total_optimise:.2f} EUR")
                st.write(f"- **Optimized margin:** {marge_optimisee:.2f} EUR")

                #if st.button("Save optimized costs"):
                    #db.yaourts.update_one(
                        #{"nom": selected_yaourt},
                        #{"$set": {
                            #"prix_ingredients": prix_ingredients_optimise,
                            #"prix_production": prix_production_optimise,
                            #"prix_vente": nouveau_prix_vente,
                            #"marge": marge_optimisee
                        #}}
                    #)
                    #st.success("Optimized costs have been saved!")
        else:
            st.error("Yogurt not found.")

def improving_costs_and_margins_page():    
    prix_ingredients = st.number_input("Enter Cost of Ingredients (in euros):", min_value=0.0, value=200.0)
    prix_production = st.number_input("Enter Production Cost (in euros):", min_value=0.0, value=300.0)
    recette = st.number_input("Enter Revenue (in euros):", min_value=0.0, value=1000.0)

    reduction_ingredients = st.slider("Reduction in Ingredient Costs (%):", min_value=0, max_value=100, value=10)
    reduction_production = st.slider("Reduction in Production Costs (%):", min_value=0, max_value=100, value=10)

    if st.button("Optimize Costs"):
        # Optimizing
        prix_ingredients_optimise, prix_production_optimise, cout_total_optimise = ameliorer_couts(
            prix_ingredients, prix_production, reduction_ingredients, reduction_production
        )

        cout_total_initial = prix_ingredients + prix_production
        marge_initiale = calculer_marge(recette, cout_total_initial)
        marge_optimisee = calculer_marge(recette, cout_total_optimise)

        # Display
        st.subheader("Results")
        st.write(f"**Initial Total Cost:** {cout_total_initial:.2f} euros")
        st.write(f"**Optimized Total Cost:** {cout_total_optimise:.2f} euros")
        st.write(f"**Initial Margin:** {marge_initiale:.2f} euros")
        st.write(f"**Optimized Margin:** {marge_optimisee:.2f} euros")

        st.subheader("Detailed Breakdown")
        st.write(f"**Optimized Ingredient Costs:** {prix_ingredients_optimise:.2f} euros")
        st.write(f"**Optimized Production Costs:** {prix_production_optimise:.2f} euros")
# endregion

# Fichiers
# region test
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

def recuperer_fichier_solidworks(db, fichier_id):
    fs = gridfs.GridFS(db)
    try:
        fichier_data = fs.get(fichier_id)
        # Créer un chemin temporaire pour enregistrer le fichier
        temp_file_path = os.path.join(tempfile.gettempdir(), fichier_data.filename)
        with open(temp_file_path, 'wb') as f:
            f.write(fichier_data.read())
        return temp_file_path
    except gridfs.NoFile:
        st.error(f"Le fichier avec l'ID {fichier_id} n'a pas été trouvé.")
        return None

def ouvrir_solidworks(chemin_fichier):
    try:
        # Créer une instance de SolidWorks
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        sw_app.Visible = True  # Rendre SolidWorks visible
        
        model = sw_app.OpenDoc(chemin_fichier, 1)  # 1 correspond à un fichier de type pièce (part)
        
        if model:
            st.success(f"Fichier {chemin_fichier} ouvert avec succès.")
        else:
            st.error(f"Impossible d'ouvrir le fichier {chemin_fichier}.")
    except Exception as e:
        st.error(f"Erreur lors de l'ouverture de SolidWorks : {e}")

def inserer_fichier_solidworks(db, projet_id, chemin_fichier):
    fs = gridfs.GridFS(db)
    try:
        with open(chemin_fichier, "rb") as f:
            fichier_id = fs.put(f, filename=chemin_fichier, projet_id=projet_id)
    except FileNotFoundError:
        st.error(f"Le fichier {chemin_fichier} n'existe pas.")
        return
    
    result = db.projets.update_one(
        {"_id": projet_id},
        {"$push": {"fichiers_solidworks": fichier_id}}
    )
    
    if result.modified_count > 0:
        st.success(f"Fichier SolidWorks inséré avec succès dans GridFS avec l'ID {fichier_id}.")
    else:
        st.error("Échec de l'insertion. Vérifiez l'ID du projet.")

def inserer_pdf_avec_gridfs(db, projet_id, chemin_pdf):
    fs = gridfs.GridFS(db)
    try:
        with open(chemin_pdf, "rb") as f:
            pdf_id = fs.put(f, filename=chemin_pdf, projet_id=projet_id)
    except FileNotFoundError:
        st.error(f"Le fichier {chemin_pdf} n'existe pas.")
        return

    result = db.projets.update_one(
        {"_id": projet_id},
        {"$set": {"pdf_file_id": pdf_id}}
    )
    
    if result.modified_count > 0:
        st.success(f"PDF inséré avec succès dans GridFS avec l'ID {pdf_id}.")
    else:
        st.error("Échec de l'insertion. Vérifiez l'ID du projet.")

def ajouter_ouvrir_fichiers():
        
    db = connection_projet()
    
    projet_id = st.text_input("Entrez l'ID du projet (par exemple : YB01) :")
    
    if projet_id:
        # insérer un fichier SolidWorks
        st.subheader("Insérer un fichier SolidWorks")
        chemin_solidworks = st.file_uploader("Choisir un fichier SolidWorks", type=["sldprt", "sldasm", "slddrw"])
        if chemin_solidworks and st.button("Insérer dans MongoDB"):
            with open(f"temp_{chemin_solidworks.name}", "wb") as f:
                f.write(chemin_solidworks.getbuffer())
            inserer_fichier_solidworks(db, projet_id, f"temp_{chemin_solidworks.name}")
        
        # insérer un fichier PDF
        st.subheader("Insérer un fichier PDF")
        chemin_pdf = st.file_uploader("Choisir un fichier PDF", type=["pdf"])
        if chemin_pdf and st.button("Insérer dans MongoDB"):
            with open(f"temp_{chemin_pdf.name}", "wb") as f:
                f.write(chemin_pdf.getbuffer())
            inserer_pdf_avec_gridfs(db, projet_id, f"temp_{chemin_pdf.name}")
        
        # récupérer et ouvrir un fichier SolidWorks
        st.subheader("Ouvrir un fichier SolidWorks depuis MongoDB")
        fichier_id_input = st.text_input("Entrez l'ID du fichier SolidWorks (ObjectId) :")
        
        if fichier_id_input:
            try:
                fichier_id = ObjectId(fichier_id_input)
                temp_file_path = recuperer_fichier_solidworks(db, fichier_id)
                if temp_file_path:
                    if st.button("Ouvrir dans SolidWorks"):
                        ouvrir_solidworks(temp_file_path)
            except Exception as e:
                st.error(f"Erreur avec l'ID du fichier : {e}")

# endregion


# Pages
CATEGORIES = {
    "General": {
        "Projects and products" : afficher_projets_et_produits,
        "Dashboard": dashboard_page,
        "Search history": rechercher_historique_page,
    },
    "Employees": {
        "Modify your information": lambda: modifier_employe_page(),
        "Add a new employee": lambda: creer_employe_page(),
        "Search an employee": lambda: rechercher_employe_page(),
    },
    "Products": {
        "Add a product": ajouter_yaourt,
        "Modify a product": modifier_yaourt_page,
        "Search a product": rechercher_yaourt_page,
    },
    "Projects": {
        "Add a new project": creer_projet_page,
        "Modify a project": modifier_projet_page,
        "Search a project": rechercher_projet_page,
    },
    "Optimisation": {
        #"Costs simulation": cost_price_simulation_page,
        "Improve costs" : improving_costs_and_margins_page,
        "Improving cost on product" : ameliorer_couts_et_marges_yaourt_page,
    },
    "Fichiers": {
        "Telecharger des PDF" : pdf_id,
        "Ajouter et ouvrir des fichiers" : ajouter_ouvrir_fichiers
    }
}

# Display et Menu
# region test
def Home():
    st.sidebar.title(f"Welcome, {st.session_state.username}!")

    selected_category = st.sidebar.selectbox("Choose a category:", list(CATEGORIES.keys()))
    selected_page = st.sidebar.radio(
        f"{selected_category} Pages:",
        list(CATEGORIES[selected_category].keys()),
    )
    
    st.session_state.selected_page = selected_page
    display_page(selected_category, selected_page)

    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.selected_page = None
        st.rerun()

def display_page(category_name, page_name):
    if category_name not in CATEGORIES or page_name not in CATEGORIES[category_name]:
        st.error(f"Page '{page_name}' not found in category '{category_name}'.")
        return

    page_content = CATEGORIES[category_name][page_name]

    st.empty()
    st.header(page_name)
    
    if callable(page_content):
        page_content()
    else:
        st.write(page_content)

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
# endregion