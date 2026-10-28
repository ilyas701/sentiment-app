# Compte rendu global des TP1 à TP6

**Binôme :** Ilyas Errifay (@ilyas701) et Othman Raji (@Othm4n)  
**Dépôt :** https://github.com/ilyas701/sentiment-app  
**Date :** 28/10/2026  

## 1. Le besoin et son cadrage

Le projet vise à automatiser l'analyse de sentiment d'un grand volume d'avis clients pour détecter rapidement les retours négatifs et prioriser le traitement par le service client. Pour répondre au Cas 3 (filtrage et priorisation d'avis de e-commerce/cinéma), nous avons retenu une approche par modélisation supervisée (Pipeline combinant TF-IDF et régression logistique). Ce choix est justifié par deux critères clés : (a) la présence de données historiques étiquetées permettant un apprentissage supervisé robuste, et (d) la conséquence d'une erreur (un faux négatif laisse passer un client mécontent sans suivi, ce qui impacte directement la rétention, d'où la nécessité d'un seuil d'incertitude prudent).

## 2. L'architecture du dépôt et le packaging (TP6)

Le dépôt est structuré de manière modulaire, suivant scrupuleusement la séparation des responsabilités et les exigences de packaging Python :
- `sentiment_app/` : Le paquet principal contenant la logique métier (`predict.py`), la gestion des versions (`__version__ = "0.6.0"`) et l'interface en ligne de commande (`cli.py` et `__main__.py`).
- `api/` : Contient le point d'entrée FastAPI (`main.py`), la gestion propre du modèle (`model.py` important directement depuis le paquet sans manipulation de `sys.path`) et les schémas de validation Pydantic (`schemas.py`).
- `ui/` : Contient l'interface Streamlit (`app.py`) et son client HTTP (`client.py`) chargé de communiquer avec l'API FastAPI.
- `data/` : Contient les jeux de données bruts, de démonstration, le fichier d'exemple pour l'analyse par lot (`data/avis_exemple.csv`) et le jeu d'or de validation (`data/jeu_or.csv` comportant 20 avis dont 5 cas difficiles).
- `models/` : Contient les artefacts de performance (`metrics.json`) et le modèle sérialisé (`sentiment.joblib`). Le fichier `metrics.json` est versionné en texte brut pour auditer instantanément les performances dans l'intégration continue, tandis que le binaire `sentiment.joblib` est généré localement ou configuré dynamiquement via la variable d'environnement `SENTIMENT_MODELE`.
- `src/` : Contient les scripts d'entraînement/évaluation et un fichier de compatibilité `predict.py` assurant le relais avec l'ancienne structure pour les tests historiques.
- `tests/` : Contient l'ensemble des tests unitaires, d'intégration, de qualité statique, de l'API, du client HTTP, de l'interface et du packaging (94 tests validés avec succès à 100%).

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
- **Qualité & CI :** Un pipeline CI (GitHub Actions) exécute à chaque commit le linter `ruff`, le vérificateur de typage statique `mypy`, les crochets `pre-commit` et la suite `pytest` avec contrôle de couverture de code (supérieure à 95% sur l'API) et validation de l'installation de la roue hors du dépôt.

## 6. L'interface Streamlit (TP5)

L'interface web Streamlit (`ui/app.py`) offre une expérience utilisateur fluide et intuitive reposant sur une architecture totalement découplée de la logique du modèle :
- **Architecture découplée (Règle d'or) :** L'interface n'importe jamais directement le modèle sérialisé (`.joblib`) ni les modules de prédiction. Elle communique exclusivement avec l'API FastAPI via la classe client `ui/client.py` (requêtes HTTP POST). Si l'API est déplacée ou si le modèle est réentraîné, l'interface n'a besoin d'aucune modification.
- **Gestion des retours et de l'incertitude :** 
  - Pour les avis clairs, le verdict (`Avis positif` ou `Avis négatif`) est affiché avec son pourcentage de confiance.
  - En cas d'abstention (score sous $0.60$), l'interface indique clairement **« Je ne sais pas : à faire vérifier par un humain »** avec un message expliquant que la confiance est sous le seuil d'abstention.
  - En cas de panne ou d'indisponibilité de l'API, la page affiche immédiatement un message d'erreur clair (« API injoignable ») au lieu d'un plantage opaque.
- **Analyse par lot (Fichier CSV) :** L'onglet « Un fichier d'avis » permet de charger un fichier CSV (comme `data/avis_exemple.csv`), d'analyser l'ensemble des lignes via l'API, d'afficher le tableau complété des verdicts et confiances, de visualiser un résumé statistique (ex: `{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}`) et de télécharger les résultats sous forme de fichier `resultats.csv`.

## 7. Packaging, CLI et Distribution (TP6)

Le projet a franchi une étape majeure d'industrialisation sous forme de paquet Python installable :
- **Paquet Python et CLI :** Le code est packagé dans `sentiment_app/` et expose une interface en ligne de commande (`sentiment`) permettant d'exécuter les actions clés (`sentiment --version`, `sentiment predict "..."`, `sentiment serve` pour l'API et `sentiment ui` pour l'interface).
- **Modèle configurable :** Grâce à la fonction `chemin_modele()` couplée à la variable d'environnement `SENTIMENT_MODELE`, le paquet peut être installé n'importe où sur le poste (hors du répertoire du dépôt) tout en localisant dynamiquement l'artefact du modèle `.joblib`.
- **Construction de la roue et tests d'intégrité :** La roue de distribution (`sentiment_app-0.6.0-py3-none-any.whl`) a été générée avec succès via l'outil `build`. Elle intègre strictement les sources nécessaires (`sentiment_app`, `api`, `ui`) en écartant les données, tests et modèles, et a été validée par un test d'installation dans un environnement virtuel tiers.
- **Épinglage des dépendances :** La version de `scikit-learn` a été épinglée en version `1.5.x` pour garantir la compatibilité binaire lors de la relecture du modèle sérialisé.

## 8. Ce qui a échoué et résolution des blocages

Les principaux blocages rencontrés durant l'ensemble des TP ont concerné :
1. La configuration initiale des chemins d'importation entre les dossiers `src/`, `tests/`, `api/` et `ui/`, entraînant des erreurs `ModuleNotFoundError` (résolues par l'ajustement du `pythonpath` dans `pytest.ini` et l'insertion explicite de la racine dans `sys.path`).
2. Des conflits de versions entre bibliothèques (notamment `pyarrow` / `mlflow` et `numpy<2`), résolus en gelant des dépendances compatibles dans `requirements.txt` et `requirements.lock`.
3. L'intégration de l'interface du TP5 : lors de l'application du kit TP5, le fichier `ui/app.py` existant avait été conservé, créant un désalignement avec les tests unitaires. L'écrasement de `ui/app.py` par la version officielle du kit a permis de valider l'ensemble des tests.
4. Le refactoring du TP6 : le déplacement de `predict.py` vers le paquet `sentiment_app/` tout en maintenant un fichier de compatibilité dans `src/` a nécessité d'ajuster les imports de l'API pour supprimer définitivement toute modification manuelle de `sys.path`.

## 9. Ce que vous feriez autrement

Dans un contexte de production industrielle, nous mettrions en place :
- Un système de gestion du cache Streamlit (`@st.cache_data`) pour éviter de recalculer inutilement les requêtes par lot lors des réexécutions de la page.
- Une surveillance de la dérive des données (*data drift*) et des performances en temps réel avec la journalisation des prédictions.
- Un ré-entraînement continu automatisé réinjectant périodiquement les avis étiquetés par la revue humaine (cas `INDETERMINE`) dans le jeu de données d'entraînement.
- Un hébergement de la roue sur un registre privé (Artifactory ou PyPI privé) pour automatiser le déploiement sur les serveurs de production.

## 10. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| Ilyas (@ilyas701) | Conception du pipeline de modélisation (TP2), configuration des tests unitaires et de qualité (ruff, mypy, pre-commit - TP4), industrialisation de l'API FastAPI (`api/` - TP3), migration du paquet et de la CLI (TP6) et intégration de la CI sur GitHub Actions. |
| Othman (@Othm4n) | Cadrage initial (TP1), développement du client HTTP et de l'interface Streamlit (`ui/` - TP5), validation des tests d'interface/client, construction de la roue `.whl`, exécution des essais hors dépôt (TP4-TP6) et rédaction des comptes-rendus. |

## Outils d'aide à la rédaction

L'assistant d'IA a été utilisé pour structurer la rédaction technique et valider la cohérence des blocs Markdown, tandis que l'ensemble des résultats chiffrés, des matrices, des tests et du code source a été produit, exécuté et vérifié par nos soins sur nos environnements locaux.
