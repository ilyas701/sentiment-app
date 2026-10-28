# Semaine 6 : le paquet, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

Voici les réponses rédigées pour compléter le fichier `docs/semaine6.md` (ou votre compte-rendu de la semaine 6) en vous basant sur vos observations pratiques lors du TP6 :


## 1. Pourquoi le modèle n'est-il pas dans la roue ? Comment le paquet le trouve-t-il ?

Le modèle entraîné (`sentiment.joblib`) n'est pas inclus dans la roue (`.whl`) car il s'agit d'un artefact d'apprentissage volumineux et non d'un composant logiciel statique (code source). La roue ne doit contenir que le code exécutable, les interfaces et les métadonnées. Pour le trouver, le paquet utilise la fonction `chemin_modele()` définie dans `sentiment_app/predict.py`, qui cherche en priorité le fichier via la variable d'environnement `SENTIMENT_MODELE` si elle est définie, ou se replie par défaut sur le chemin relatif `models/sentiment.joblib` à la racine du projet.


## 2. Qu'est-ce qui a changé dans api/model.py quand predict() est entré dans le paquet, et pourquoi est-ce mieux ?

Lorsque `predict()` a été intégré au paquet `sentiment_app`, nous avons supprimé de `api/model.py` toutes les instructions de bidouillage manuel des chemins (`sys.path.insert(...)` et `RACINE = ...`), ainsi que les imports directs depuis le dossier `src/`. L'API importe désormais proprement ses fonctions directement depuis le paquet installé (`from sentiment_app.predict import ...`). C'est beaucoup mieux car le code respecte les standards de packaging Python : le service API est totalement découplé de la structure interne des dossiers du dépôt et s'appuie sur une installation propre des dépendances.


## 3. La roue installée hors du dépôt : qu'a-t-il fallu lui fournir, et pourquoi scikit-learn est-il épinglé dans pyproject.toml ?

Lors de l'installation de la roue dans un environnement neuf hors du dépôt, il a fallu lui fournir explicitement le chemin du modèle entraîné via la variable d'environnement `SENTIMENT_MODELE`, car l'artefact n'est pas embarqué dans le paquet. Par ailleurs, `scikit-learn` est épinglé dans `pyproject.toml` (version 1.5.x) car un modèle sérialisé (`.joblib`) avec une version spécifique de scikit-learn est étroitement lié à la bibliothèque qui l'a produit. Sans cet épinglage, une mise à jour mineure de la bibliothèque lors du rechargement de la roue provoquerait des incompatibilités de désérialisation (ex: `AttributeError` sur les objets du classifieur).
