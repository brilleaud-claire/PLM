from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def connection_historique():
    uri = "mongodb+srv://clairebrilleaud:t2VbmN0VZS4qNClQ@yahourt.q5y6i.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Yahourt"
    # Créer un nouveau client et se connecter au serveur
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Test de connexion
    try:
        client.admin.command('ping')
        print("Pingé avec succès. Connexion à MongoDB réussie !")
    except Exception as e:
        print(e)

    # Connexion à la base de données
    db = client["yaourt_database"]

    return db

db = connection_historique()

def creer_historique_modification(
    db, 
    type_document,        # "yaourt" ou autre type de document (projet, employes...)
    document_id,          # ID du document modifié
    ancienne_version,     # Dictionnaire avec les anciennes données
    nouvelle_version,     # Dictionnaire avec les nouvelles données
    modification_date,    # Date de la modification
    employee_id           # ID de l'employé ayant effectué la modification
):
    """
    Crée un historique de modification et l'insère dans la base de données MongoDB.
    
    Les informations sont fournies sous forme de paramètres.
    """
    historique = {
        "type": type_document,  # Type du document modifié (ex: "yaourt")
        "document_id": document_id,  # ID du document modifié
        "ancienne_version": ancienne_version,  # Ancienne version du document
        "nouvelle_version": nouvelle_version,  # Nouvelle version du document
        "modification_date": modification_date,  # Date de la modification
        "employee_id": employee_id  # ID de l'employé ayant effectué la modification
    }

    # Insertion dans la collection d'historique
    result = db.historique.insert_one(historique)
    print(f"Historique de modification créé avec succès ! ID : {result.inserted_id}")

db = connection_historique()

# Exemple de données
"""""
ancienne_version = {
    "nom": "Yaourt à boire Tarte Tatin",
    "version": "v1.0",
    "prix_vente": 2.30
}

nouvelle_version = {
    "nom": "Yaourt à boire Tarte Tatin",
    "version": "v1.1",
    "prix_vente": 2.50
}

modification_date = "2024-11-29"
employee_id = "EM_Bernard"
document_id = "YBTT001"

creer_historique_modification(
    db, 
    type_document="yaourt", 
    document_id=document_id, 
    ancienne_version=ancienne_version, 
    nouvelle_version=nouvelle_version, 
    modification_date=modification_date, 
    employee_id=employee_id
)
"""

def modifier_historique(
    db, 
    historique_id,         # ID de l'historique à modifier
    updates,               # Dictionnaire avec les champs à mettre à jour
    employee_id           # ID de l'employé effectuant la modification
):
    """
    Modifie un historique de modification dans la base de données MongoDB.
    """
    # Rechercher l'historique dans la base
    historique = db.historique.find_one({"_id": historique_id})
    
    if not historique:
        raise ValueError("Historique introuvable. Vérifiez l'ID.")
    
    # Afficher les informations actuelles pour référence
    print("\n=== Historique actuel ===")
    for key, value in historique.items():
        print(f"{key}: {value}")
    
    # Mise à jour des champs spécifiques
    if not updates:
        print("Aucune modification fournie.")
        return

    # Mise à jour du champ "last_modification"
    updates["employee_id"] = employee_id

    # Appliquer les modifications à MongoDB
    db.historique.update_one({"_id": historique_id}, {"$set": updates})
    print("L'historique a été mis à jour avec succès.")

def chercher_historique_par_id(db, historique_id):
    """
    Recherche un historique de modification par son ID dans la base de données MongoDB.
    Retourne l'objet historique si trouvé, sinon None.
    """
    historique = db.historique.find_one({"_id": historique_id})
    
    if historique:
        return historique
    else:
        print("Historique introuvable avec cet ID.")
        return None

def chercher_historique_par_document_id(db, document_id):
    """
    Recherche l'historique des modifications d'un document spécifique.
    Retourne une liste des objets historiques trouvés.
    """
    historiques = list(db.historique.find({"document_id": document_id}))
    
    if historiques:
        return historiques
    else:
        print(f"Aucun historique trouvé pour le document ID : {document_id}.")
        return []

def chercher_historique_par_date_modification(db, date_modification):
    """
    Recherche les historiques de modification effectués à une date spécifique.
    Retourne une liste des objets historiques trouvés.
    """
    historiques = list(db.historique.find({"modification_date": date_modification}))
    
    if historiques:
        return historiques
    else:
        print(f"Aucun historique trouvé pour la date de modification : {date_modification}.")
        return []

def chercher_historique_par_employee_id(db, employee_id):
    """
    Recherche les historiques de modifications effectuées par un employé spécifique.
    Retourne une liste des objets historiques trouvés.
    """
    historiques = list(db.historique.find({"employee_id": employee_id}))
    
    if historiques:
        return historiques
    else:
        print(f"Aucun historique trouvé pour l'employé avec ID : {employee_id}.")
        return []

