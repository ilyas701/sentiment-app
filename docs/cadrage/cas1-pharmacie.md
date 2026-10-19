## Besoin en une phrase (obligatoire)
Signaler au pharmacien toute ordonnance à laquelle il manque un champ obligatoire[cite: 10, 10].

## Utilisateur final (obligatoire)
Le pharmacien d'officine lors de la délivrance des médicaments.

## Approche retenue (obligatoire)
Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)
(b) La vérifiabilité et l'explicabilité sont exigées pour chaque contrôle légal d'une ordonnance. (a) Aucune base d'ordonnances étiquetées n'est disponible au départ. (d) Une erreur de validation a des conséquences graves sur la santé du patient[cite: 10].

## Données nécessaires et leur origine (obligatoire)
Les schémas réglementaires des ordonnances et la liste des champs obligatoires définis par la loi.

## Métrique de succès et seuil d'acceptation (obligatoire)
Un taux de rappel de 100 % sur la détection des champs obligatoires manquants.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)
Un faux négatif laisse passer une ordonnance invalide. Une validation humaine obligatoire par le pharmacien reste indispensable avant toute délivrance.

## Risques éthiques ou de confidentialité (obligatoire)
Protection stricte des données de santé personnelles (RGPD / secrets médicaux).

## Approche écartée et pourquoi (facultatif)
Le machine learning a été écarté car l'erreur critique ne tolère aucune approximation statistique et requiert des règles logiques strictes.
