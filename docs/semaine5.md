# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface Streamlit agit exclusivement en tant que client HTTP : elle communique avec le service via le module `ui/client.py` en envoyant des requêtes à l'API FastAPI (`POST /predict`), sans jamais accéder directement au modèle sérialisé ou aux fonctions internes. Cette séparation stricte des responsabilités (3ᵉ règle d'architecture du projet) garantit que l'interface et le modèle sont totalement découplés. Ainsi, si le modèle est réentraîné, remplacé ou hébergé sur un autre serveur distant, l'interface web continue de fonctionner à l'identique sans qu'aucune modification de son code ne soit nécessaire.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Lorsque le score de confiance renvoyé par l'API se situe sous le seuil d'abstention (fixé à 0,60), l'interface affiche l'étiquette **« Je ne sais pas : à faire vérifier par un humain »** ainsi qu'un encadré bleu précisant que la confiance est insuffisante. C'est bien meilleur qu'un verdict forcé car cela évite d'attribuer de façon automatisée une catégorie potentiellement erronée à un avis ambigu ou mal compris (comme lors d'ironie ou de tournures complexes). En isolant ces cas limites pour une revue humaine, le système sécurise la qualité des décisions métiers et protège la relation client.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

Si l'API FastAPI est arrêtée ou injoignable, l'interface intercepte l'erreur de connexion au démarrage (ou lors d'une réexécution) et affiche un message d'erreur rouge explicite en haut de la page : **« API injoignable : lancez d'abord uvicorn api.main:app »**. 

Lors du traitement par lot du fichier `data/avis_exemple.csv`, le résumé indique la répartition `{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}` : il y a donc **1 avis sur les 6** (l'avis inventé `xqzvb wlkptr grombu`) qui passe sous le seuil d'abstention et part vers une vérification humaine.
