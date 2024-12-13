from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def connection_stock():
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

db = connection_stock()

def creer_stock(db, id_stock, produit_id, quantite):
    """
    Crée un document de stock dans la base de données MongoDB.
    
    produit_id : ID du produit (par exemple, yaourt123)
    quantite : Quantité d'unités en stock (par exemple, 500)
    """

    # Vérification de l'unicité de l'ID du projet
    if id_stock:
        if db.yaourts.find_one({"_id": id_stock}):
            raise ValueError(f"L'ID {id_stock} existe déjà. Veuillez en fournir un autre.")
    
    stock = {
        "_id": id_stock,
        "produit_id": produit_id,
        "quantite": quantite
    }

    # Insertion dans la collection de stock
    result = db.stock.insert_one(stock)
    print(f"Stock créé avec succès ! ID : {result.inserted_id}")

db = connection_stock()

# Exemple de données
""""
id_stock = "YBTT"
produit_id = "YBTT001"
quantite = 500

creer_stock(db, id_stock, produit_id, quantite)
"""

def modifier_stock(db, stock_id, nouvelle_quantite):
    """
    Modifie la quantité en stock d'un produit spécifique dans la base de données MongoDB.
    
    stock_id : ID du document de stock à modifier
    nouvelle_quantite : La nouvelle quantité à mettre à jour
    """
    # Vérification si le stock existe
    stock = db.stock.find_one({"_id": stock_id})
    
    if not stock:
        raise ValueError("Stock introuvable. Vérifiez l'ID.")

    # Mise à jour de la quantité
    db.stock.update_one({"_id": stock_id}, {"$set": {"quantite": nouvelle_quantite}})
    print(f"Stock mis à jour avec succès. Nouvelle quantité : {nouvelle_quantite}")

def ajuster_stock(db, stock_id, quantite_ajustee):
    """
    Ajuste la quantité de stock en ajoutant ou en soustrayant des unités.
    
    stock_id : ID du document de stock à ajuster
    quantite_ajustee : Nombre d'unités à ajouter ou soustraire (peut être négatif)
    """
    # Vérification si le stock existe
    stock = db.stock.find_one({"_id": stock_id})
    
    if not stock:
        raise ValueError("Stock introuvable. Vérifiez l'ID.")
    
    # Calcul de la nouvelle quantité
    nouvelle_quantite = stock["quantite"] + quantite_ajustee
    
    if nouvelle_quantite < 0:
        raise ValueError("La quantité de stock ne peut pas être inférieure à zéro.")
    
    # Mise à jour de la quantité
    db.stock.update_one({"_id": stock_id}, {"$set": {"quantite": nouvelle_quantite}})
    print(f"Stock ajusté avec succès. Nouvelle quantité : {nouvelle_quantite}")


def chercher_stock_par_id(db, stock_id):
    """
    Recherche un document de stock par son ID dans la base de données MongoDB.
    Retourne l'objet stock si trouvé, sinon None.
    """
    stock = db.stock.find_one({"_id": stock_id})
    
    if stock:
        return stock
    else:
        print("Stock introuvable avec cet ID.")
        return None

def chercher_stock_par_produit_id(db, produit_id):
    """
    Recherche un document de stock par l'ID du produit dans la base de données MongoDB.
    Retourne l'objet stock si trouvé, sinon None.
    """
    stock = db.stock.find_one({"produit_id": produit_id})
    
    if stock:
        return stock
    else:
        print(f"Aucun stock trouvé pour le produit ID : {produit_id}.")
        return None


def chercher_tous_stocks_par_produit_id(db, produit_id):
    """
    Recherche tous les documents de stock liés à un produit spécifique.
    Retourne une liste des objets stocks trouvés.
    """
    stocks = list(db.stock.find({"produit_id": produit_id}))
    
    if stocks:
        return stocks
    else:
        print(f"Aucun stock trouvé pour le produit ID : {produit_id}.")
        return []
