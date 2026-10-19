## Besoin en une phrase (obligatoire)
Répondre aux questions des employés sur le règlement intérieur en citant explicitement les articles correspondants[cite: 10, 10].

## Utilisateur final (obligatoire)
Les salariés de l'entreprise recherchant des informations sur leurs droits et devoirs.

## Approche retenue (obligatoire)
Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)
(b) La vérifiabilité est impérative car chaque réponse doit citer précisément sa source légale dans le document. (a) Il n'y a pas de questions étiquetées à grande échelle au départ[cite: 10]. (c) Le volume des requêtes reste modéré[cite: 10].

## Données nécessaires et leur origine (obligatoire)
Le document textuel officiel du règlement intérieur de l'entreprise.

## Métrique de succès et seuil d'acceptation (obligatoire)
Un taux de pertinence des sources citées supérieur à 95 % évalué sur un jeu de questions-réponses test.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)
Une mauvaise orientation d'un employé peut créer un litige interne mineur ; un accès aux RH est prévu en cas de doute persistant.

## Risques éthiques ou de confidentialité (obligatoire)
Confidentialité des clauses internes de l'entreprise et des éventuelles questions individuelles posées par les collaborateurs.

## Approche écartée et pourquoi (facultatif)
Le modèle génératif seul a été écarté en raison des risques d'hallucination inacceptables sur un document juridique interne.
