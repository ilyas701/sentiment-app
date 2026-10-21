# Compte rendu global des TP1 à TP5

**Binôme :** Ilyas Errifay (@ilyas701) et Othman Raji(@Othm4n)  
**Dépôt :** https://github.com/ilyas701/sentiment-app  
**Date :** 21/10/2026  

## 1. Le besoin et son cadrage

Le projet vise à automatiser l'analyse de sentiment d'un grand volume d'avis clients pour détecter rapidement les retours négatifs et prioriser le traitement par le service client. Pour répondre au Cas 3 (filtrage et priorisation d'avis de e-commerce/cinéma), nous avons retenu une approche par modélisation supervisée (Pipeline combinant TF-IDF et régression logistique). Ce choix est justifié par deux critères clés : (a) la présence de données historiques étiquetées permettant un apprentissage supervisé robuste, et (d) la conséquence d'une erreur (un faux négatif leaves passer un client mécontent sans suivi, ce qui impacte directement la rétention, d'où la nécessité d'un seuil d'incertitude prudent).

## 2. L'architecture du dépôt

Le dépôt est structuré de manière modulaire, suivant scrupuleusement la séparation des responsabilités :
- `api/` : Contient le point d'entrée FastAPI (`main.py`), la gestion du modèle (`model.py`) et les schémas de validation Pydantic (`schemas.py`).
- `ui/` : Contient l'interface Streamlit (`app.py`) et son client HTTP (`client.py`) chargé de communiquer avec l'API FastAPI.
- `data/` : Contient les jeux de données bruts, de démonstration, le fichier d'exemple pour l'analyse par lot (`data/avis_exemple.csv`) et le jeu d'or de validation (`data/jeu_or.csv` comportant 20 avis dont 5 cas difficiles).
- `models/` : Contient les artefacts de performance (`metrics.json`) et le modèle sérialisé (`sentiment.joblib`). Le fichier `metrics.json` est versionné en texte brut pour auditer instantanément les performances dans l'intégration continue, tandis que le binaire `sentiment.joblib` est généré localement.
- `src/` : Contient la logique métier, la génération de données de démonstration, l'entraînement et la fonction de prédiction.
- `tests/` : Contient l'ensemble des tests unitaires, d'intégration, de qualité statique, de l'API, du client HTTP et de l'interface Streamlit (88 tests passés avec succès à 100%).

## 3. Le modèle

Le pipeline s'appuie sur une vectorisation TF-IDF du texte suivie d'un classifieur linéaire (régression logistique) entraîné sur le jeu de données Allociné et évalué sur notre jeu de démonstration.

| Jeu | Avis | Vocabulaire | F1 macro | Rappel négatif |
| --- | --- | --- | --- | --- |
| Démonstration | 290 | 316 | 0.879 | 0.900 |
| Allociné | 20000 | 10000+ | 0.920 | 0.915 |

**Matrice de confusion (Jeu de démonstration) :**
```text
[[27,  2],
 [ 5, 24]]
```
- Vrais Négatifs ($27$) : Avis négatifs correctement classés.
- Faux Positifs ($2$) : Avis positifs classés à tort comme négatifs (surcoût mineur de vérification humaine).
- Faux Négatifs ($5$) : Avis négatifs classés à tort comme positifs (risque critique de non-prise en charge du client).
- Vrais Positifs ($24$) : Avis positifs correctement identifiés.

## 4. L'analyse des erreurs

Sur le jeu de test de démonstration et le jeu d'or, nous observons que les erreurs proviennent principalement de tournures ironiques ou de négations complexes que le modèle bag-of-words (TF-IDF) interprète mal. *Exemple :* L'avis « Pas déçu du tout, je recommande » ou des phrases à retournement d'avis mitigés sont complexes pour un sac de mots. Pour corriger cela, il faudrait basculer vers des modèles contextuels profonds (type Transformers/CamemBERT), ce qui n'était pas l'objectif didactique de cette séance axée sur la mise en place d'un pipeline MLOps léger, robuste et itératif.

## 5. Industrialisation (API FastAPI), Qualité et Seuil d'Abstention

- **API FastAPI :** Le modèle est encapsulé dans un service FastAPI (`api/main.py`), exposant les endpoints `/health` (santé du service et modèle chargé) et `/predict` (classification des avis). L'API intègre un contrat Pydantic strict d'entrée (`schemas.py`) rejetant les textes vides, composés uniquement d'espaces ou dépassant 2000 caractères par des erreurs HTTP 422 standardisées.
- **Seuil d'abstention :** Un seuil de confiance de $0.60$ (`SEUIL_ABSTENTION`) a été implémenté dans `api/model.py`. En dessous de ce seuil, le verdict renvoyé est `INDETERMINE`, permettant d'orienter les cas incertains vers une revue humaine plutôt que d'imposer un diagnostic binaire erroné.
- **Qualité & CI :** Un pipeline CI (GitHub Actions) exécute à chaque commit le linter `ruff`, le vérificateur de typage statique `mypy`, les crochets `pre-commit` et la suite `pytest` avec contrôle de couverture de code (supérieure à 95% sur l'API).

## 6. L'interface Streamlit (TP5)

L'interface web Streamlit (`ui/app.py`) offre une expérience utilisateur fluide et intuitive reposant sur une architecture totalement découplée de la logique du modèle :
- **Architecture découplée (Règle d'or) :** L'interface n'importe jamais directement le modèle sérialisé (`.joblib`) ni les modules de prédiction du TP2. Elle communique exclusivement avec l'API FastAPI via la classe client `ui/client.py` (requêtes HTTP POST). Si l'API est déplacée ou si le modèle est réentraîné, l'interface n'a besoin d'aucune modification.
- **Gestion des retours et de l'incertitude :** 
  - Pour les avis clairs, le verdict (`Avis positif` ou `Avis négatif`) est affiché avec son pourcentage de confiance.
  - En cas d'abstention (score sous $0.60$), l'interface indique clairement **« Je ne sais pas : à faire vérifier par un humain »** avec un message expliquant que la confiance est sous le seuil d'abstention.
  - En cas de panne ou d'indisponibilité de l'API, la page affiche immédiatement un message d'erreur clair (« API injoignable ») au lieu d'un plantage opaque.
- **Analyse par lot (Fichier CSV) :** L'onglet « Un fichier d'avis » permet de charger un fichier CSV (comme `data/avis_exemple.csv`), d'analyser l'ensemble des lignes via l'API, d'afficher le tableau complété des verdicts et confiances, de visualiser un résumé statistique (ex: `{'INDETERMINE': 2, 'NEGATIVE': 2, 'POSITIVE': 2}`) et de télécharger les résultats sous forme de fichier `resultats.csv`.

## 7. Ce qui a échoué et résolution des blocages

Les principaux blocages rencontrés durant l'ensemble des TP ont concerné :
1. La configuration initiale des chemins d'importation entre les dossiers `src/`, `tests/`, `api/` et `ui/`, entraînant des erreurs `ModuleNotFoundError` (résolues par l'ajustement du `pythonpath` dans `pytest.ini` et l'insertion explicite de la racine dans `sys.path`).
2. Des conflits de versions entre bibliothèques (notamment `pyarrow` / `mlflow` et `numpy<2`), résolus en gelant des dépendances compatibles dans `requirements.txt` et `requirements.lock`.
3. L'intégration de l'interface du TP5 : lors de l'application du kit TP5, le fichier `ui/app.py` existant avait été conservé, créant un désalignement avec les 5 tests unitaires de `tests/test_interface.py`. L'écrasement forcé de `ui/app.py` par la version officielle du kit a permis de valider à 100% l'intégralité de la suite de tests (88 passed).

## 8. Ce que vous feriez autrement

Dans un contexte de production industrielle, nous mettrions en place :
- Un système de gestion du cache Streamlit (`@st.cache_data`) pour éviter de recalculer inutilement les requêtes par lot lors des réexécutions de la page.
- Une surveillance de la dérive des données (*data drift*) et des performances en temps réel avec la journalisation des prédictions.
- Un ré-entraînement continu automatisé réinjectant périodiquement les avis étiquetés par la revue humaine (cas `INDETERMINE`) dans le jeu de données d'entraînement.

## 9. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| Ilyas (@ilyas701) | Conception du pipeline de modélisation (TP2), configuration des tests unitaires et de qualité (ruff, mypy, pre-commit - TP4), industrialisation de l'API FastAPI (`api/` - TP3) et intégration de la CI sur GitHub Actions. |
| Othmane (@Othm4n) | Cadrage initial (TP1), développement du client HTTP et de l'interface Streamlit (`ui/` - TP5), validation des tests d'interface/client, exécution des essais locaux et rédaction des comptes-rendus. |

## Outils d'aide à la rédaction

L'assistant d'IA a été utilisé pour structurer la rédaction technique et valider la cohérence des blocs Markdown, tandis que l'ensemble des résultats chiffrés, des matrices, des tests et du code source a été produit, exécuté et vérifié par nos soins sur nos environnements locaux.
