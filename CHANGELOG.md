# Journal des versions

Le numéro de version suit les TP : 0.N.0 à la fin du TP N. Chaque version publiée porte une étiquette Git `v0.N.0`.

## 0.6.0 (TP6) : le paquet

- Le paquet Python est installable depuis une roue et fournit la commande `sentiment` (`--version`, `predict`, `serve`, `ui`).
- Le modèle reste un artefact séparé, configurable avec `SENTIMENT_MODELE` ; l'API importe maintenant le prédicteur depuis `sentiment_app`.
- La roue exclut les tests, les données et le modèle ; la CI la construit et vérifie son installation hors du dépôt avec scikit-learn 1.5.

## 0.5.0 (TP5) : l'interface

- Page Streamlit : un avis, ou un fichier d'avis ; le client HTTP traduit chaque réponse de l'API.

## 0.4.0 (TP4) : tests et qualité

- Contrat d'entrée testé, abstention `INDETERMINE`, jeu d'or, tests d'intégration, contrat typé, ruff, mypy, pre-commit.

## 0.3.0 (TP3) : l'API

- FastAPI : `/health`, `/predict`, contrat Pydantic ; la CI entraîne le modèle avant les tests.

## 0.2.0 (TP2) : le modèle

- TF-IDF et régression logistique ; les métriques sont versionnées, le modèle ne l'est pas.

## 0.1.0 (TP1) : le cadrage

- Environnement Python 3.11, structure du dépôt, trois fiches de cadrage, dépôt GitHub à deux auteurs.
