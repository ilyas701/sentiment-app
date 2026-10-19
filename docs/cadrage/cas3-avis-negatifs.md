## Besoin en une phrase (obligatoire)
Remonter automatiquement les avis clients négatifs en tête de file pour traiter en priorité les clients mécontents[cite: 4, 10].

## Utilisateur final (obligatoire)
L'équipe relation client et les agents de support technique.

## Approche retenue (obligatoire)
Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)
(a) Des données étiquetées sont disponibles gratuitement et en grand nombre via les notes numériques associées aux avis[cite: 10]. (c) Le volume quotidien se chiffre en milliers d'avis, rendant l'analyse manuelle impossible[cite: 10]. (d) L'erreur de classification a une conséquence faible et réversible[cite: 10].

## Données nécessaires et leur origine (obligatoire)
Un historique textuel d'avis clients et leurs notes de notation (ex: de 1 à 5 étoiles).

## Métrique de succès et seuil d'acceptation (obligatoire)
Atteindre un rappel d'au moins 0,90 sur la classe négative et un score F1 macro supérieur à 0,85[cite: 11, 15].

## Conséquence d'une erreur et validation humaine prévue (obligatoire)
Un faux négatif retarde le traitement d'un client insatisfait. Une vérification finale reste assurée par l'agent lors de la lecture de l'avis.

## Risques éthiques ou de confidentialité (obligatoire)
Anonymisation requise des données personnelles (noms, coordonnées) qui pourraient figurer dans les corps de texte des commentaires.

## Approche écartée et pourquoi (facultatif)
L'approche par règles métier a été écartée car la variabilité du vocabulaire des clients ne permet pas d'établir une liste exhaustive de mots-clés.
