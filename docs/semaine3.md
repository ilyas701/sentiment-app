# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

1. Pourquoi l'API refuse-t-elle de démarrer sans models/sentiment.joblib, plutôt que de démarrer et de répondre 503 ?
Le choix de bloquer le démarrage au lancement (via le chargement synchrone ou dans l'événement de démarrage) permet de garantir qu'aucun trafic n'est accepté si l'application n'est pas dans un état fonctionnel. Cela évite de déployer une instance "zombie" ou partiellement cassée qui renverrait des erreurs 503 à répétition, et permet de détecter immédiatement une anomalie de configuration ou l'absence du fichier modèle dès la phase de build ou de déploiement (fail-fast).

2. Un texte vide est refusé deux fois : par Pydantic, puis par predict(). Est-ce redondant ?
Oui, cela peut paraître redondant d'un point de vue fonctionnel, mais c'est une excellente pratique de robustesse en MLOps (principe de la défense en profondeur). Pydantic agit comme un premier filtre strict au niveau de l'interface de l'API pour rejeter les requêtes malformées avant même qu'elles n'atteignent la logique métier. La validation interne dans predict() garantit quant à elle que la fonction de prédiction reste sûre et indépendante, pouvant être appelée de manière autonome (par exemple dans des scripts, des batchs ou des tests unitaires) sans risquer de propager des données corrompues.
