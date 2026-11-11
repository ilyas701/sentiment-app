# Journal des versions

Ce fichier suit la convention « majeure.mineure.correctif » : un changement incompatible
(fonction renommée, étiquette changée) augmente le premier chiffre. Chaque version publiée porte
une étiquette Git `vX.Y.Z`.

Les versions 0.1.0 à 0.6.0 suivaient l'ancienne numérotation des TP (TP 1 à TP 6). La version 1.0.0
termine le volume 1 du manuel, dans la numérotation du programme (Atelier 0, TP 1 à TP 4).

## [1.0.0] - 2026-11-11

### Ajouté
- API `/v1` (TP 2) : `/v1/health`, `/v1/predict`, `/v1/modele` ; clé d'API dans l'en-tête `X-API-Key`,
  rôles `client` et `admin`, format d'erreur unique ; `/predict` sans version marquée dépréciée.
- Client web (`web/`, 12 tests Node) et service Spring Boot qui consomme l'API (`java/avis-service/`).
- Interface Streamlit (TP 3) : appelle `/v1` avec la clé lue dans `.env` ; deux graphiques, répartition
  des verdicts et distribution de la confiance.
- Paquet `sentiment-app` (TP 4) : fonction `predict(texte)`, qui renvoie
  `{"label": "positive" | "negative", "score": float}` ; commande `sentiment "texte"`, options `--json`
  et `--version`, code de retour 2 sur un texte vide ; modèle de démonstration embarqué dans la roue.

### Modifié
- Le paquet est dans `src/sentiment_app/` et embarque le modèle ; la version est écrite dans
  `pyproject.toml`. Changement incompatible avec 0.6.0 : les sous-commandes `predict`, `serve` et `ui`
  et la variable `SENTIMENT_MODELE` disparaissent ; l'API et l'interface se lancent avec `uvicorn`
  et `streamlit run`.

### Limites connues
- Modèle entraîné sur 290 avis : sensible aux avis mitigés et aux négations.
- Le paquet ne s'abstient pas : le seuil d'abstention (0,65) est appliqué par l'API seulement.
- Le modèle n'est garanti qu'avec scikit-learn 1.5 (dépendance figée).

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
