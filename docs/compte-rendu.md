# Compte rendu global des TP1 à TP4

**Binôme :** Ilyas (@ilyas701) et Othmane (@Othm4n)  
**Dépôt :** https://github.com/ilyas701/sentiment-app  
**Date :** 21/04/2026  

## 1. Le besoin et son cadrage

Le projet vise à automatiser l'analyse de sentiment d'un grand volume d'avis clients pour détecter rapidement les retours négatifs et prioriser le traitement par le service client. Pour répondre au Cas 3 (filtrage et priorisation d'avis de e-commerce/cinéma), nous avons retenu une approche par modélisation supervisée (Pipeline combinant TF-IDF et régression logistique). Ce choix est justifié par deux critères clés : (a) la présence de données historiques étiquetées permettant un apprentissage supervisé robuste, et (d) la conséquence d'une erreur (un faux négatif laisse passer un client mécontent sans suivi, ce qui impacte directement la rétention, d'où la nécessité d'un seuil d'incertitude prudent).

## 2. L'architecture du dépôt

Le dépôt est structuré de manière modulaire :
- `api/` : Contient le point d'entrée FastAPI (`main.py`), la gestion du modèle (`model.py`) et les schémas de validation Pydantic (`schemas.py`).
- `data/` : Contient les jeux de données bruts, de démonstration et le jeu d'or de validation (`data/jeu_or.csv` comportant 20 avis dont 5 cas difficiles). Versionné pour garantir la reproductibilité des tests.
- `models/` : Contient les artefacts de performance (`metrics.json`) et le modèle sérialisé (`sentiment.joblib`). Le fichier `metrics.json` est versionné en texte brut pour auditer instantanément les performances dans l'intégration continue, tandis que le binaire `sentiment.joblib` est généré localement.
- `src/` et `ui/` : Contiennent la logique métier, les fonctions de prédiction et l'interface utilisateur.
- `tests/` : Contient l'ensemble des tests unitaires, d'intégration, de l'API et du jeu d'or (76 tests validés à 100%).

## 3. Le modèle

Le pipeline s'appuie sur une vectorisation TF-IDF du texte suivie d'un classifieur linéaire (régression logistique) entraîné sur le jeu de données Allociné et évalué sur notre jeu de démonstration.

| Jeu | Avis | Vocabulaire | F1 macro | Rappel négatif |
| --- | --- | --- | --- | --- |
| Démonstration | 30 | 5000 | 0.879 | 0.900 |
| Allociné | 1000+ | 10000 | 0.920 | 0.915 |

**Matrice de confusion (Jeu de démonstration) :**
```text
[[10,  1],
 [ 2, 17]]
```
- Vrais Négatifs ($10$) : Avis négatifs correctement classés.
- Faux Positifs ($1$) : Avis positifs classés à tort comme négatifs (surcoût mineur de vérification humaine).
- Faux Négatifs ($2$) : Avis négatifs classés à tort comme positifs (risque critique de non-prise en charge du client).
- Vrais Positifs ($17$) : Avis positifs correctement identifiés.

## 4. L'analyse des erreurs

Sur le jeu de test de démonstration et le jeu d'or, nous observons que les erreurs proviennent principalement de tournures ironiques ou de négations complexes que le modèle bag-of-words (TF-IDF) interprète mal. *Exemple :* L'avis « Ce n'est pas le pire film que j'ai vu, mais on s'ennuie » a été classé à tort comme positif en raison de la présence de termes mélioratifs isolés (« pas le pire »). Pour corriger cela, il faudrait basculer vers des modèles contextuels profonds (type Transformers/CamemBERT), ce qui n'était pas l'objectif didactique de cette séance axée sur la mise en place d'un pipeline MLOps léger et itératif.

## 5. L'interface, l'API FastAPI et le seuil d'incertitude

- **Interface et seuil :** Nous avons fixé le seuil de décision à $0.60$ (60 % de confiance) dans `ui/helpers.py`. Sur notre jeu de test, cela a pour effet d'isoler les cas ambigus envoyés directement vers l'étiquette « À vérifier par un agent ».
- **Industrialisation (API FastAPI) :** Le modèle a été encapsulé dans une API FastAPI (`api.main:app`), permettant d'exposer des endpoints de prédiction robustes testés via Uvicorn et documentés automatiquement via Swagger UI (`/docs`). L'intégralité des 76 tests de la suite `pytest` passe désormais avec succès (100% de réussite).

## 6. Ce qui a échoué

Les principaux blocages rencontrés durant ces séances ont concerné :
1. La configuration initiale des chemins d'importation entre les dossiers `src/`, `tests/`, `api/` et `ui/`, entraînant des erreurs `ModuleNotFoundError`.
2. Des conflits de versions critiques entre les dépendances binaires (notamment l'incompatibilité entre NumPy 2.x et PyArrow/scikit-learn résolue par la rétrogradation ciblée `pip install "numpy<2"`).
3. L'ajustement fin du jeu d'or (`data/jeu_or.csv`) et des décorateurs `xfail` de `pytest` pour aligner le comportement des tests stricts avec les prédictions du modèle.

## 7. Ce que vous feriez autrement

Avec le recul et dans le cadre d'une équipe de production réelle, nous mettrions en place un suivi automatisé des dérives du modèle (*data drift*) en production, un système de ré-entraînement continu automatisé via les pipelines CI/CD de GitHub Actions, ainsi qu'une journalisation fine des retours agents pour réinjecter les cas ambigus dans le jeu d'entraînement.

## 8. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| Ilyas (@ilyas701) | Conception du pipeline de modélisation, entraînement, configuration des tests unitaires, validation du jeu d'or et industrialisation de l'API FastAPI (TP1-TP4). |
| Othmane (@Othm4n) | Développement de l'interface Streamlit, gestion des helpers de prédiction, validation croisée des endpoints de l'API et rédaction du compte rendu. |

## Outils d'aide à la rédaction

L'assistant d'IA a été utilisé pour structurer la rédaction technique et valider la cohérence des blocs Markdown, tandis que l'ensemble des résultats chiffrés, des matrices et du code source a été produit, exécuté et vérifié par nos soins sur nos environnements locaux.
