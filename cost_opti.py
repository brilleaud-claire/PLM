
def calculer_marge(recette, cout_total):
    return recette - cout_total

def ameliorer_couts(prix_ingredients, prix_production, reduction_ingredients, reduction_production):
    prix_ingredients_optimise = prix_ingredients * (1 - reduction_ingredients / 100)
    prix_production_optimise = prix_production * (1 - reduction_production / 100)
    cout_total_optimise = prix_ingredients_optimise + prix_production_optimise
    return prix_ingredients_optimise, prix_production_optimise, cout_total_optimise