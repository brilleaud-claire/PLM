from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def connection_employe():
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

db = connection_employe()

def creer_employe(db, employee_id, level_access, job_title, password):
    """
    Crée un nouvel employé et l'insère dans la base de données MongoDB.
    """

    # Création du document employé
    employe = {
        "_id": employee_id,  # Assignation de l'_id personnalisé ici
        "level_access": level_access,
        "job_title": job_title,
        "password": password  # Toujours stocker les mots de passe hashés
    }

    # Insertion dans la base de données
    result = db.employes.insert_one(employe)
    print(f"Employé créé avec succès ! ID : {result.inserted_id}")

#creer_employe(db, employee_id="EM_Bernard", level_access=2, job_title="Responsable Marketing", password="1234")

def modifier_employe(db, employee_id, updates):
    """
    Modifie un employé existant dans la base de données MongoDB.
    
    Paramètres :
        - db : Connexion à la base de données MongoDB.
        - employee_id : ID de l'employé à modifier.
        - updates : Dictionnaire contenant les champs à mettre à jour et leurs nouvelles valeurs.
    """
    # Rechercher l'employé dans la base
    employe = db.employes.find_one({"_id": employee_id})
    
    if not employe:
        raise ValueError("Employé introuvable. Vérifiez l'ID.")
    
    # Mise à jour des champs spécifiques
    if "password" in updates:
        # Hashage du mot de passe avant de l'insérer
        updates["password"] = sha256(updates["password"].encode()).hexdigest()

    # Appliquer les modifications à MongoDB
    db.employes.update_one({"_id": employee_id}, {"$set": updates})
    print(f"L'employé avec l'ID {employee_id} a été mis à jour avec succès.")


def chercher_employe_par_id(db, employee_id):
    """
    Recherche un employé par son ID dans la base de données MongoDB.
    Retourne l'objet employé si trouvé, sinon None.
    """
    employe = db.employes.find_one({"_id": employee_id})
    
    if employe:
        return employe
    else:
        print("Employé introuvable avec cet ID.")
        return None

def chercher_employe_par_job_title(db, job_title):
    """
    Recherche les employés par leur titre de poste dans la base de données MongoDB.
    Retourne une liste des objets employés trouvés.
    """
    employes = list(db.employes.find({"job_title": job_title}))
    
    if employes:
        return employes
    else:
        print(f"Aucun employé trouvé pour le titre de poste : {job_title}.")
        return []

def chercher_employe_par_level_access(db, level_access):
    """
    Recherche les employés par leur niveau d'accès dans la base de données MongoDB.
    Retourne une liste des objets employés trouvés.
    """
    employes = list(db.employes.find({"level_access": level_access}))
    
    if employes:
        return employes
    else:
        print(f"Aucun employé trouvé pour le niveau d'accès : {level_access}.")
        return []

def modifier_id_employe(db):
    """
    Modifie l'ID d'un employé existant dans la base de données MongoDB.
    """
    # Demander l'ID actuel de l'employé sous forme de chaîne
    ancien_id = input("Entrez l'ID de l'employé dont vous voulez changer l'_id : ")

    # Rechercher l'employé avec cet _id
    employe = db.employes.find_one({"_id": ancien_id})
    
    if not employe:
        print("Employé introuvable. Vérifiez l'ID.")
        return

    print("\n=== Employé actuel ===")
    for key, value in employe.items():
        print(f"{key}: {value}")
    
    # Demander le nouvel _id
    nouveau_id = input("Entrez le nouvel ID pour cet employé : ")

    # Créer un nouveau document avec le nouvel _id
    nouveau_employe = employe.copy()  # Copier l'ancien employé
    nouveau_employe["_id"] = nouveau_id  # Modifier l'_id

    # Insérer le nouvel employé avec le nouvel _id
    db.employes.insert_one(nouveau_employe)
    print(f"Employé créé avec succès sous le nouvel ID : {nouveau_id}")

    # Supprimer l'ancien document
    db.employes.delete_one({"_id": ancien_id})
    print(f"L'ancien employé avec l'ID {ancien_id} a été supprimé.")

def chercher_employes_par_modification_date(db, date_modification):
    """
    Recherche les employés modifiés à une date spécifique.
    Retourne une liste des objets employés trouvés.
    """
    employes = list(db.employes.find({"last_modification.date": {"$gte": datetime.strptime(date_modification, "%Y-%m-%d")}}))
    
    if employes:
        return employes
    else:
        print(f"Aucun employé trouvé pour la date de dernière modification : {date_modification}.")
        return []
