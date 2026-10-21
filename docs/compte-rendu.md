# Compte rendu global des TP1 à TP3

**Binôme :** Ilyas (@ilyas701) et Othmane (@Othm4n)  
**Dépôt :** https://github.com/ilyas701/sentiment-app  
**Date :** 21/04/2026  

## 1. Le besoin et son cadrage

Le projet vise à automatiser l'analyse de sentiment d'un grand volume d'avis clients pour détecter rapidement les retours négatifs et prioriser le traitement par le service client. Pour répondre au Cas 3 (filtrage et priorisation d'avis de e-commerce/cinéma), nous avons retenu une approche par modélisation supervisée (Pipeline combinant TF-IDF et régression logistique). Ce choix est justifié par deux critères clés : (a) la présence de données historiques étiquetées permettant un apprentissage supervisé robuste, et (d) la conséquence d'une erreur (un faux négatif laisse passer un client mécontent sans suivi, ce qui impacte directement la rétention, d'où la nécessité d'un seuil d'incertitude prudent).

## 2. L'architecture du dépôt

Le dépôt est structuré de manière modulaire :
- `data/` : Contient les jeux de données bruts et de démonstration (`sample_reviews.csv`, `demo_reviews.csv`). Versionné pour garantir la reproductibilité des tests d'interface.
- `models/` : Contient les artefacts de performance (`metrics.json`). **Pourquoi `models/metrics.json` est dans Git alors que `models/sentiment.joblib` ne l'est pas ?** Le fichier `metrics.json` est léger, versionnable en texte brut et permet d'auditer instantanément les performances de validation dans l'intégration continue sans alourdir le dépôt. À l'inverse, `sentiment.joblib` est un binaire lourd généré localement lors de l'entraînement (via le script de build), évitant ainsi le versionnage de fichiers volumineux sujets à des conflits de fusion.
- `src/` et `ui/` : Contiennent la logique métier et l'application Streamlit.
- `tests/` : Contient l'ensemble des tests unitaires et d'interface (45 tests validés).

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

Sur le jeu de test de démonstration, nous observons 3 erreurs principales (1 faux positif et 2 faux négatifs). Ces erreurs proviennent principalement de tournures ironiques ou de négations complexes que le modèle bag-of-words (TF-IDF) interprète mal. *Exemple :* L'avis « Ce n'est pas le pire film que j'ai vu, mais on s'ennuie » a été classé à tort comme positif en raison de la présence de termes mélioratifs isolés (« pas le pire »). Pour corriger cela, il faudrait basculer vers des modèles contextuels profonds (type Transformers/CamemBERT), ce qui n'était pas l'objectif didactique de cette séance axée sur la mise en place d'un pipeline MLOps léger et itératif.

## 5. L'interface et le seuil d'incertitude

Nous avons fixé le seuil de décision à $0.60$ (60 % de confiance) dans `ui/helpers.py`. Sur notre jeu de test, cela a pour effet d'isoler 7 cas ambigus envoyés directement vers l'étiquette « À vérifier par un agent ». Ce compromis paraît idéal du point de vue de la relation client : il évite d'automatiser des décisions incertaines tout en réduisant considérablement la charge de travail humaine par rapport à une relecture intégrale manuelle.

## 6. Ce qui a échoué

Les principaux blocages rencontrés durant ces trois séances ont concerné la configuration initiale des chemins d'importation entre les dossiers `src/`, `tests/` et `ui/`, entraînant des erreurs `ModuleNotFoundError` sous pytest. Un autre temps fort de débogage a impliqué la synchronisation des versions de librairies dans l'environnement virtuel `.venv`. Nous les avons résolus en structurant proprement le fichier `setup.py` / `pyproject.toml` et en utilisant des chemins relatifs robustes basés sur `pathlib`.

## 7. Ce que vous feriez autrement

Avec le recul et dans le cadre d'une équipe de production réelle, nous mettrions en place un suivi automatisé des dérives du modèle (*data drift*) en production, un système de ré-entraînement continu automatisé via les pipelines CI/CD de GitHub Actions, ainsi qu'une journalisation fine des retours agents pour réinjecter les cas ambigus dans le jeu d'entraînement.

## 8. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| Ilyas (@ilyas701) | Conception du pipeline de modélisation, entraînement, configuration des tests unitaires (TP1-TP2) et intégration continue. |
| Othmane (@Othm4n) | Développement de l'interface Streamlit, gestion des helpers de prédiction, design des métriques et rédaction du compte rendu. |

## Outils d'aide à la rédaction

L'assistant d'IA a été utilisé pour structurer la rédaction technique et valider la cohérence des blocs Markdown, tandis que l'ensemble des résultats chiffrés, des matrices et du code source a été produit, exécuté et vérifié par nos soins sur nos environnements locaux.
