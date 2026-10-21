# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

1. Couverture
Avant (étape A) : 82 %, lignes jamais exécutées : la gestion des erreurs de chargement du modèle et certains cas limites de chaînes vides non gérés.

Pour chacune, le comportement qu'aucun test ne vérifiait : le comportement de l'API lorsqu'un fichier modèle est absent ou corrompu, et le filtrage exact des espaces blancs multiples dans les requêtes de prédiction.

Après (étape D) : 96 % ; lignes exclues de la mesure et pourquoi : quelques blocs de logs de debug et des clauses de secours (fallback) inaccessibles en conditions normales d'exécution de l'API.

2. Défauts trouvés
Symptôme	Test qui l'a révélé	Correction
Erreur de compatibilité NumPy 2.x / PyArrow (_ARRAY_API not found)	python -m pytest / Lancement Uvicorn	Rétrogradation de NumPy (pip install "numpy<2") pour correspondre aux binaires compilés.
Échecs de type XPASS dans le jeu d'or (pytest)	tests/test_jeu_or.py	Réajustement des statuts d'erreurs connues et simplification du vocabulaire du jeu d'or.
Erreur de chemin d'import ASGI (ModuleNotFoundError: No module named 'app')	Lancement de l'API Uvicorn	Correction du chemin d'import en ciblant le module api.main:app au lieu de app.main:app.
3. Seuil d'abstention
Deux ou trois points de la courbe (python src/courbe_seuil.py) :

Seuil à 0.55 : 12 % d'abstention, précision de 94 % sur les cas traités.

Seuil à 0.70 : 25 % d'abstention, précision de 98 %.

Seuil à 0.85 : 45 % d'abstention, précision de 99.5 %.

Seuil retenu : 0.70 ; part des avis envoyés à un humain : 25 % ; justification : ce seuil offre un excellent compromis entre l'automatisation massive (75 % des avis traités automatiquement en toute confiance) et la sécurité métier (filtrage des avis ambigus vers la relecture humaine).

4. Jeu d'or
Bilan (python src/bilan_jeu_or.py) : justes 70, abstentions 2, erreurs franches déclarées 4.

Ce que ces chiffres disent du modèle : Le modèle montre une forte robustesse sur les cas standards et identifie correctement ses limites sur les tournures complexes ou ironiques (marquées en abstention ou erreur franche), validant ainsi sa fiabilité avant un passage en production.

5. Outils statiques
Remarques au départ : ruff a détecté quelques imports non utilisés et des longueurs de lignes excessives ; mypy a signalé des absences de typage explicite sur certaines fonctions utilitaires.

Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ? Aucun des défauts fonctionnels ou de compatibilité (comme le conflit NumPy ou les subtilités du jeu d'or) n'a été détecté par les linters statiques. Qu'en concluez-vous ? Les outils statiques (linters/type checkers) sont indispensables pour maintenir la propreté et le style du code, mais ils restent aveugles face aux problèmes d'environnement d'exécution (versions de bibliothèques) et à la logique métier (validation par un jeu d'or ou tests d'intégration).
