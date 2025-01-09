
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def connection_yahourt():
    uri = "mongodb+srv://clairebrilleaud:t2VbmN0VZS4qNClQ@yahourt.q5y6i.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Yahourt"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    #test1
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # Connexion à MongoDB
    db = client["yaourt_database"]

    return db

db = connection_yahourt()

#test2
from datetime import datetime

def creer_yaourt(
    db, 
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
    date_mise_production, 
    date_peremption, 
    description, 
    produit_valide, 
    marketing_valide, 
    employee_id, 
    projet_id=None,
    date_mise_vente=None
):
    """
    Crée un nouveau yaourt et l'insère dans la base de données MongoDB.
    
    Les informations du yaourt sont fournies sous forme de paramètres.
    """
    # Calcul de la marge
    marge = prix_vente - (prix_ingredients + prix_production)

    # Vérification de l'unicité de l'ID du projet
    if projet_id:
        if db.yaourts.find_one({"_id": projet_id}):
            raise ValueError(f"L'ID {projet_id} existe déjà. Veuillez en fournir un autre.")
    
    # Création du document yaourt
    yaourt = {
        "_id": projet_id,  # Assignation de l'_id personnalisé ici
        "nom": nom, #Tarte tatin
        "version": version, #1.0
        "recette": recette, # ingrédients séparés par une virgule
        "volume": volume, # en ml (juste le chiffre)
        "level_access": level_access, # un ou deux
        "materiaux_emballage": materiaux_emballage, #ex: verre et carton recyclé
        "temps_fabrication": temps_fabrication, # en minutes
        "prix_ingredients": prix_ingredients, 
        "prix_production": prix_production,
        "prix_vente": prix_vente,
        "marge": marge,
        "date_mise_production": date_mise_production, #AAAA-MM-JJ
        "date_mise_vente": date_mise_vente, #AAAA-MM-JJ
        "date_peremption": date_peremption, #AAAA-MM-JJ
        "description": description,
        "validation": {
            "produit": produit_valide, #booléen
            "marketing": marketing_valide #booléen
        },
        "projet_id": projet_id,
        "last_modification": {
            "employee_id": employee_id,
            "date": datetime.utcnow()
        }
    }

    # Insertion dans la base de données
    result = db.yaourts.insert_one(yaourt)
    print(f"Yaourt créé avec succès ! ID : {result.inserted_id}")



# Exemple d'appel de la fonction
#creer_yaourt(db)

from datetime import datetime

def modifier_yaourt(
    db, 
    yaourt_id, 
    updates, 
    employee_id
):
    """
    Modifie un yaourt existant dans la base de données MongoDB.
    
    Paramètres :
        - db : Connexion à la base de données MongoDB.
        - yaourt_id : ID du yaourt à modifier.
        - updates : Dictionnaire contenant les champs à mettre à jour et leurs nouvelles valeurs.
        - employee_id : ID de l'employé effectuant la modification.
    
    Comment utiliser ce code ?
        updates = {
            "nom": "Yaourt Fraise Réinventé",
            "prix_vente": 1.5,
            "description": "Une version améliorée du yaourt à la fraise.",
            "validation.produit": True,
            "validation.marketing": False
        }

        # Appel de la fonction
        modifier_yaourt(
            db=db,
            yaourt_id="YBF001",
            updates=updates,
            employee_id="EM_Bernard"
        )
    """
    # Rechercher le yaourt dans la base
    yaourt = db.yaourts.find_one({"_id": yaourt_id})
    
    if not yaourt:
        raise ValueError("Yaourt introuvable. Vérifiez l'ID.")
    
    # Afficher les informations actuelles pour référence (si nécessaire)
    print("\n=== Yaourt actuel ===")
    for key, value in yaourt.items():
        print(f"{key}: {value}")
    
    # Mise à jour des champs spécifiques
    if not updates:
        print("Aucune modification fournie.")
        return

    # Recalculer la marge si les prix changent
    if any(key in updates for key in ["prix_vente", "prix_ingredients", "prix_production"]):
        prix_vente = updates.get("prix_vente", yaourt.get("prix_vente"))
        prix_ingredients = updates.get("prix_ingredients", yaourt.get("prix_ingredients"))
        prix_production = updates.get("prix_production", yaourt.get("prix_production"))
        updates["marge"] = prix_vente - (prix_ingredients + prix_production)

    # Mise à jour du champ "last_modification"
    updates["last_modification"] = {
        "employee_id": employee_id,
        "date": datetime.utcnow()
    }

    # Appliquer les modifications à MongoDB
    db.yaourts.update_one({"_id": yaourt_id}, {"$set": updates})
    print("Le yaourt a été mis à jour avec succès.")

""""
def modifier_yaourt(db):
    
    #Modifie un yaourt existant dans la base de données MongoDB.
    
    # Demander l'ID du yaourt à modifier
    yaourt_id = input("Entrez l'ID du yaourt à modifier : ")
    
    # Rechercher le yaourt dans la base
    yaourt = db.yaourts.find_one({"_id": yaourt_id})
    
    if not yaourt:
        print("Yaourt introuvable. Vérifiez l'ID.")
        return
    
    print("\n=== Yaourt actuel ===")
    for key, value in yaourt.items():
        print(f"{key}: {value}")

    print("\nQuels champs voulez-vous modifier ? (laisser vide pour ne pas modifier un champ)")

    # Demande des nouvelles valeurs pour chaque champ
    updates = {}
    nom = input("Nom : ")
    if nom:
        updates["nom"] = nom
    
    version = input("Version (exemple : v1.1) : ")
    if version:
        updates["version"] = version
    
    recette = input("Recette (ingrédients séparés par des virgules) : ")
    if recette:
        updates["recette"] = recette
    
    volume = input("Volume (en ml) : ")
    if volume:
        updates["volume"] = float(volume)
    
    level_access = input("Level access : ")
    if level_access:
        updates["level_access"] = int(level_access)
    
    materiaux_emballage = input("Matériaux de l'emballage : ")
    if materiaux_emballage:
        updates["materiaux_emballage"] = materiaux_emballage
    
    temps_fabrication = input("Temps de fabrication (en minutes) : ")
    if temps_fabrication:
        updates["temps_fabrication"] = int(temps_fabrication)
    
    prix_ingredients = input("Prix des ingrédients (en euros) : ")
    if prix_ingredients:
        updates["prix_ingredients"] = float(prix_ingredients)
    
    prix_production = input("Prix de production (en euros) : ")
    if prix_production:
        updates["prix_production"] = float(prix_production)
    
    prix_vente = input("Prix de vente (en euros) : ")
    if prix_vente:
        updates["prix_vente"] = float(prix_vente)
    
    if "prix_vente" in updates or "prix_ingredients" in updates or "prix_production" in updates:
        # Recalculer la marge si les prix changent
        updates["marge"] = updates.get("prix_vente", yaourt["prix_vente"]) - (
            updates.get("prix_ingredients", yaourt["prix_ingredients"]) + 
            updates.get("prix_production", yaourt["prix_production"])
        )
    
    date_mise_production = input("Date de mise en production (AAAA-MM-JJ) : ")
    if date_mise_production:
        updates["date_mise_production"] = date_mise_production
    
    date_mise_vente = input("Date de mise en vente (AAAA-MM-JJ, ou appuyez sur Entrée si pas encore mise en vente) : ")
    if date_mise_vente:
        updates["date_mise_vente"] = date_mise_vente
    
    date_peremption = input("Date de péremption (AAAA-MM-JJ) : ")
    if date_peremption:
        updates["date_peremption"] = date_peremption
    
    description = input("Description : ")
    if description:
        updates["description"] = description
    
    produit_valide = input("Validation produit (oui/non) : ")
    if produit_valide:
        updates["validation.produit"] = produit_valide.lower() == "oui"
    
    marketing_valide = input("Validation marketing (oui/non) : ")
    if marketing_valide:
        updates["validation.marketing"] = marketing_valide.lower() == "oui"
    
    projet_id = input("ID du projet associé : ")
    if projet_id:
        updates["projet_id"] = projet_id
    
    # Mise à jour du champ last_modification
    employee_id = input("Votre ID employé : ")
    if employee_id:
        updates["last_modification"] = {
            "employee_id": employee_id,
            "date": datetime.utcnow()
        }
    
    # Appliquer les modifications à MongoDB
    if updates:
        db.yaourts.update_one({"_id": yaourt_id}, {"$set": updates})
        print("Le yaourt a été mis à jour avec succès.")
    else:
        print("Aucune modification appliquée.")

#modifier_yaourt(db)
"""
#modifier_yaourt(db,"YBTT001",{"projet_id":"YB01"},"EM_Bernard")
def modifier_id_yaourt(db):
    """
    Modifie un yaourt existant dans la base de données MongoDB.
    """
    # Demander l'ID actuel du yaourt sous forme de chaîne
    ancien_id = input("Entrez l'ID du yaourt dont vous voulez changer l'_id : ")

    # Rechercher le yaourt avec cet _id
    yaourt = db.yaourts.find_one({"_id": ancien_id})
    
    if not yaourt:
        print("Yaourt introuvable. Vérifiez l'ID.")
        return

    print("\n=== Yaourt actuel ===")
    for key, value in yaourt.items():
        print(f"{key}: {value}")
    
    # Demander le nouvel _id
    nouveau_id = input("Entrez le nouvel ID pour ce yaourt : ")

    # Créer un nouveau document avec le nouvel _id
    nouveau_yaourt = yaourt.copy()  # Copier l'ancien yaourt
    nouveau_yaourt["_id"] = nouveau_id  # Modifier l'_id

    # Insérer le nouveau yaourt avec le nouvel _id
    db.yaourts.insert_one(nouveau_yaourt)
    print(f"Yaourt créé avec succès sous le nouvel ID : {nouveau_id}")

    # Supprimer l'ancien document
    db.yaourts.delete_one({"_id": ancien_id})
    print(f"L'ancien yaourt avec l'ID {ancien_id} a été supprimé.")

#modifier_id_yaourt(db)

def chercher_yaourt_par_id(yaourt_id):
    """
    Recherche un yaourt par son ID dans la base de données MongoDB.
    Retourne l'objet yaourt si trouvé, sinon None.
    """
    
    yaourt = db.yaourts.find_one({"_id": yaourt_id})
    
    if yaourt:
        return yaourt
    else:
        print("Yaourt introuvable avec cet ID.")
        return None

def chercher_yaourts_par_date_production(db, date_production):
    """
    Recherche les yaourts produits à une date spécifique.
    Retourne une liste des objets yaourts trouvés.
    """
    yaourts = list(db.yaourts.find({"date_mise_production": date_production}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour la date de production : {date_production}.")
        return []

def chercher_yaourts_par_date_peremption(db, date_peremption):
    """
    Recherche les yaourts à la date de peremption certaine à une date spécifique.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"date_peremption": date_peremption}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour la date de production : {date_peremption}.")
        return []

def chercher_yaourts_par_date_vente(db, date_vente):
    """
    Recherche les yaourts à la date de mise en vente certaine à une date spécifique.
    Retourne une liste des objets yaourts trouvés.
    """
    #date_vente = input("Entrez la date de peremption (AAAA-MM-JJ) : ")
    
    yaourts = list(db.yaourts.find({"date_mise_vente": date_vente}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour la date de production : {date_vente}.")
        return []

def chercher_yaourts_par_nom(db, nom):
    """
    Recherche les yaourts avec un certain nom.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"nom": nom}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour le nom : {nom}.")
        return []

def chercher_yaourts_par_validation_produit(db, produit_valide):
    """
    Recherche les yaourts validés ou non en fonction du critère de validation produit.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"validation.produit": produit_valide}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour validation produit = {'oui' if produit_valide else 'non'}.")
        return []

def chercher_yaourts_par_validation_marketing(db, marketing_valide):
    """
    Recherche les yaourts validés ou non en fonction du critère de validation marketing.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"validation.marketing": marketing_valide}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour validation marketing = {'oui' if marketing_valide else 'non'}.")
        return []

def chercher_yaourts_par_derniere_modification_date(db, date_modification):
    """
    Recherche les yaourts modifiés à une date spécifique.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"last_modification.date": {"$gte": datetime.strptime(date_modification, "%Y-%m-%d")}}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour la date de dernière modification : {date_modification}.")
        return []

def chercher_yaourts_par_employee_id_modification(db, employee_id):
    """
    Recherche les yaourts modifiés par un employé spécifique.
    Retourne une liste des objets yaourts trouvés.
    """
    
    yaourts = list(db.yaourts.find({"last_modification.employee_id": employee_id}))
    
    if yaourts:
        return yaourts
    else:
        print(f"Aucun yaourt trouvé pour l'employé avec ID : {employee_id}.")
        return []



