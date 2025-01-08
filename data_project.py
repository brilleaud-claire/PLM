from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

def connection_projet():
    uri = "mongodb+srv://clairebrilleaud:t2VbmN0VZS4qNClQ@yahourt.q5y6i.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Yahourt"
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["yaourt_database"]
    return db

db = connection_projet()

def creer_projet(
    db, 
    projet_id, 
    nom, 
    version, 
    level_access, 
    date_debut, 
    date_fin, 
    budget, 
    recette, 
    description, 
    employee_id
):
    """
    Crée un nouveau projet et l'insère dans la collection projets.
    """
    projet = {
        "_id": projet_id,
        "nom": nom,
        "version": version,
        "level_access": level_access,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "budget": budget,
        "recette": recette,
        "description": description,
        "last_modification": {
            "employee_id": employee_id,
            "date": datetime.utcnow()
        }
    }

    # Vérification de l'unicité de l'ID
    if db.projets.find_one({"_id": projet_id}):
        raise ValueError(f"Le projet avec l'ID {projet_id} existe déjà. Veuillez en fournir un autre.")

    # Insertion dans MongoDB
    result = db.projets.insert_one(projet)
    print(f"Projet créé avec succès ! ID : {result.inserted_id}")

#creer_projet(db,"YB01","Yahourt à boire","v1.0",1,"2022-01-01","2024-01-01",10000000,1000000000000,"On est riche","EM_Bernard")

def modifier_projet(
    db, 
    projet_id, 
    updates, 
    employee_id
):
    """
    Modifie un projet existant dans la collection projets.
    """
    projet = db.projets.find_one({"_id": projet_id})
    if not projet:
        raise ValueError("Projet introuvable. Vérifiez l'ID.")

    if not updates:
        print("Aucune modification fournie.")
        return

    # Mise à jour de la dernière modification
    updates["last_modification"] = {
        "employee_id": employee_id,
        "date": datetime.utcnow()
    }

    db.projets.update_one({"_id": projet_id}, {"$set": updates})
    print("Projet mis à jour avec succès.")

def chercher_projet_par_id(db, projet_id):
    """
    Recherche un projet par son ID.
    """
    projet = db.projets.find_one({"_id": projet_id})
    if projet:
        return projet
    else:
        print("Projet introuvable.")
        return None

def chercher_projets_par_date_debut(db, date_debut):
    """
    Recherche les projets ayant une date de début spécifique.
    """
    projets = list(db.projets.find({"date_debut": date_debut}))
    if projets:
        return projets
    else:
        print(f"Aucun projet trouvé pour la date de début : {date_debut}.")
        return []

def chercher_projets_par_date_fin(db, date_fin):
    """
    Recherche les projets ayant une date de fin spécifique.
    """
    projets = list(db.projets.find({"date_fin": date_fin}))
    if projets:
        return projets
    else:
        print(f"Aucun projet trouvé pour la date de fin : {date_fin}.")
        return []

def chercher_projets_par_budget(db, budget_min, budget_max):
    """
    Recherche les projets avec un budget compris entre budget_min et budget_max.
    """
    projets = list(db.projets.find({"budget": {"$gte": budget_min, "$lte": budget_max}}))
    if projets:
        return projets
    else:
        print(f"Aucun projet trouvé avec un budget entre {budget_min} et {budget_max}.")
        return []

def chercher_projets_par_employee_id_modification(db, employee_id):
    """
    Recherche les projets modifiés par un employé spécifique.
    """
    projets = list(db.projets.find({"last_modification.employee_id": employee_id}))
    if projets:
        return projets
    else:
        print(f"Aucun projet trouvé pour l'employé avec ID : {employee_id}.")
        return []

def chercher_projets_par_recette(db, recette_min, recette_max):
    """
    Recherche les projets avec une recette comprise entre recette_min et recette_max.
    """
    projets = list(db.projets.find({"recette": {"$gte": recette_min, "$lte": recette_max}}))
    if projets:
        return projets
    else:
        print(f"Aucun projet trouvé avec une recette entre {recette_min} et {recette_max}.")
        return []


import gridfs

def inserer_pdf_avec_gridfs(db, projet_id, chemin_pdf):
    """
    Insère un fichier PDF dans MongoDB en utilisant GridFS.
    
    Args:
        db: La connexion à la base de données MongoDB.
        yaourt_id: L'ID du projet auquel associer le PDF.
        chemin_pdf: Le chemin du fichier PDF à insérer.
    """
    # Initialiser GridFS
    fs = gridfs.GridFS(db)

    # Lire le fichier PDF
    try:
        with open(chemin_pdf, "rb") as f:
            pdf_id = fs.put(f, filename=chemin_pdf, projet_id=projet_id)
    except FileNotFoundError:
        print(f"Le fichier {chemin_pdf} n'existe pas.")
        return

    # Ajouter une référence au PDF dans le document du yaourt
    result = db.projets.update_one(
        {"_id": projet_id},
        {"$set": {"pdf_file_id": pdf_id}}
    )
    
    if result.modified_count > 0:
        print(f"PDF inséré avec succès dans GridFS avec l'ID {pdf_id}.")
    else:
        print("Échec de l'insertion. Vérifiez l'ID du projet.")

# Exemple d'utilisation
#inserer_pdf_avec_gridfs(db, "YB01", "C:/Users/clair/Downloads/EBOM-YBF0001.pdf")

def recuperer_pdf_avec_gridfs(db, pdf_id, chemin_sortie):
    """
    Récupère un fichier PDF stocké dans MongoDB GridFS.
    
    Args:
        db: La connexion à la base de données MongoDB.
        pdf_id: L'ID du fichier dans GridFS.
        chemin_sortie: Le chemin où sauvegarder le fichier PDF.
    """
    fs = gridfs.GridFS(db)
    try:
        pdf_data = fs.get(pdf_id)
        with open(chemin_sortie, "wb") as f:
            f.write(pdf_data.read())
        print(f"PDF sauvegardé avec succès à : {chemin_sortie}")
    except gridfs.NoFile:
        print("Fichier introuvable dans GridFS.")

# Exemple
#recuperer_pdf_avec_gridfs(db, pdf_id, "sortie/fichier.pdf")

def inserer_image_avec_gridfs(db, projet_id, chemin_image):
    """
    Insère une image dans MongoDB en utilisant GridFS et met à jour le projet correspondant.
    
    Args:
        db: La connexion à la base de données MongoDB.
        projet_id: L'ID du projet auquel associer l'image.
        chemin_image: Le chemin de l'image à insérer.
    """
    import gridfs

    # Initialiser GridFS
    fs = gridfs.GridFS(db)

    # Lire le fichier image
    try:
        with open(chemin_image, "rb") as f:
            image_id = fs.put(f, filename=chemin_image, projet_id=projet_id)
    except FileNotFoundError:
        print(f"Le fichier {chemin_image} n'existe pas.")
        return

    # Ajouter une référence à l'image dans le document du projet
    result = db.projets.update_one(
        {"_id": projet_id},
        {"$set": {"image_file_id": image_id}}
    )
    
    if result.modified_count > 0:
        print(f"Image insérée avec succès dans GridFS avec l'ID {image_id}.")
    else:
        print("Échec de l'insertion. Vérifiez l'ID du projet.")


def recuperer_image_avec_gridfs(db, image_id, chemin_sortie):
    """
    Récupère une image stockée dans MongoDB GridFS et la sauvegarde localement.
    
    Args:
        db: La connexion à la base de données MongoDB.
        image_id: L'ID de l'image dans GridFS.
        chemin_sortie: Le chemin où sauvegarder l'image.
    """
    import gridfs

    fs = gridfs.GridFS(db)
    try:
        image_data = fs.get(image_id)
        with open(chemin_sortie, "wb") as f:
            f.write(image_data.read())
        print(f"Image sauvegardée avec succès à : {chemin_sortie}")
    except gridfs.NoFile:
        print("Image introuvable dans GridFS.")

inserer_image_avec_gridfs(db, "YB01", "C:/Users/clair/Downloads/image.png")