# sentiment-app

Classe un avis client rédigé en français : `positive` ou `negative`, avec une confiance entre 0,5 et 1.

## Installation

Téléchargez la roue depuis la release `v1.0.0` du dépôt GitHub, puis :

    pip install sentiment_app-1.0.0-py3-none-any.whl

Le modèle est inclus dans la roue : rien d'autre à télécharger.

## Exemples

En ligne de commande :

    sentiment "Livraison rapide, très satisfait"          # positive (confiance 77%)
    sentiment --json "Produit cassé et service injoignable, à fuir"
    sentiment --version

Un texte vide est refusé avec le code de retour 2.

En Python :

    from sentiment_app import predict
    predict("Colis abîmé")   # {'label': 'negative', 'score': ...}

## Limites

- Modèle de démonstration (TF-IDF et régression logistique, 290 avis, F1 macro 0,879) : sensible aux avis
  mitigés et aux négations (« pas déçu du tout »).
- Le paquet renvoie toujours `positive` ou `negative`. L'API du dépôt ajoute un seuil d'abstention
  (`INDETERMINE` sous 0,65) : sans un tel seuil, ne pas utiliser ce modèle pour décider seul.
- Le modèle n'est garanti qu'avec scikit-learn 1.5, dépendance figée à l'installation.
- Le modèle est un fichier joblib : n'installez la roue que depuis la release officielle du dépôt,
  car charger un fichier joblib peut exécuter du code.
