# Compte rendu global : Atelier 0 et TP 1 à TP 4

**Binôme :** Ilyas Errifay (@ilyas701) et Othman Raji (@Othm4n)  
**Dépôt :** https://github.com/ilyas701/sentiment-app  
**Version livrée :** release `v1.0.0` (https://github.com/ilyas701/sentiment-app/releases/tag/v1.0.0)  
**Date :** 25/11/2026  

> **Numérotation.** Le dépôt a d'abord été construit avec l'ancienne numérotation (TP1 à TP6, versions 0.1.0 à 0.6.0). Ce compte rendu suit celle du programme et du manuel : Atelier 0 (ancien TP1), TP 1 (anciens TP2 et TP3), TP 2 (API `/v1`, nouveau), TP 3 (ancien TP5), TP 4 (ancien TP6, refait en 1.0.0). L'ancien TP4 (tests aux limites, abstention, jeu d'or, ruff, mypy) est un travail en plus, conservé.

## 1. Le besoin et son cadrage

Le projet vise à automatiser l'analyse de sentiment d'un grand volume d'avis clients pour détecter rapidement les retours négatifs et prioriser le traitement par le service client. Pour répondre au Cas 3 (filtrage et priorisation d'avis), nous avons retenu une approche supervisée (TF-IDF et régression logistique). Deux critères justifient ce choix : (a) la présence de données historiques étiquetées, et (d) la conséquence d'une erreur : un faux négatif laisse un client mécontent sans suivi, d'où la nécessité d'un seuil d'abstention prudent.

## 2. L'architecture du dépôt

- `src/sentiment_app/` : le **paquet installable 1.0.0** : `predict()`, la commande `sentiment` (`cli.py`) et le modèle, copié dans `modele/` au moment de construire la roue.
- `src/` : les scripts `train.py`, `evaluate.py`, `courbe_seuil.py` et `predict.py`, la fonction de prédiction appelée par l'API.
- `api/` : FastAPI : `main.py` (format d'erreur, CORS, route `/predict` dépréciée), `v1.py` (routes `/v1`), `securite.py` (clés et rôles), `model.py` (seuil d'abstention) et `schemas.py` (contrat Pydantic).
- `ui/` : l'interface Streamlit (`app.py`) et son client HTTP (`client.py`).
- `web/` : un client web sans dépendance et ses 12 tests Node.
- `java/avis-service/` : un service Spring Boot qui consomme l'API (5 tests JUnit).
- `scripts/verifier_livrable.py` : contrôle du livrable du TP 4, comme le fait le correcteur.
- `tests/` : **128 tests Python verts** (1 ignoré dans le dépôt, `test_paquet.py`, lancé par le vérificateur sur la roue installée), couverture de `api/` à **100 %**.

La CI GitHub Actions rejoue trois jobs à chaque push : Python (ruff, mypy, pytest avec couverture minimale de 95 %), client web (Node) et service Java (Maven).

## 3. Le modèle

Le pipeline vectorise le texte avec TF-IDF, puis applique une régression logistique.

| Jeu | Avis | Vocabulaire | F1 macro | Rappel négatif |
| --- | --- | --- | --- | --- |
| Démonstration | 290 | 316 | 0.879 | 0.931 |
| Allociné | 20000 | 10000+ | 0.920 | 0.915 |

**Matrice de confusion (jeu de démonstration, 58 avis de test) :**
```text
[[27,  2],
 [ 5, 24]]
```
Les lignes sont les vraies classes, dans l'ordre `negative`, `positive` (rappel négatif : 27 / 29 = 0,931). **2 avis négatifs sont classés positifs** : c'est l'erreur la plus coûteuse pour notre besoin, un client mécontent qui passe inaperçu, et c'est elle que l'abstention doit réduire. Les 5 avis positifs classés négatifs ne coûtent qu'une vérification inutile.

## 4. L'analyse des erreurs

Les erreurs viennent surtout des négations et des avis mitigés, qu'un sac de mots (TF-IDF) ne sait pas lire. « Pas déçu du tout, je recommande » obtient un score de 0,618 seulement : le modèle voit « déçu » et hésite. « Le design est joli mais la fonctionnalité laisse à désirer », négatif dans notre jeu d'or, est classé positif avec 0,61. Un modèle contextuel (type CamemBERT) corrigerait une partie de ces cas, mais ce n'était pas l'objectif du volume 1.

## 5. TP 1 : l'API FastAPI et le seuil d'abstention

- **API :** `/health` et `/predict`, avec un contrat Pydantic qui refuse en 422 un texte vide, fait d'espaces ou de plus de 2000 caractères.
- **Seuil d'abstention : 0,65** (`SEUIL_ABSTENTION` dans `api/model.py`). Sous ce seuil, l'API renvoie `INDETERMINE` et l'avis va à un humain. Nous avons choisi cette valeur avec `src/courbe_seuil.py` sur les 58 avis de test : à 0,65, l'API décide seule pour 41 avis (71 %) avec 1 erreur, contre 7 erreurs sans abstention ; à 0,60 (valeur du manuel), elle décide pour 42 avis avec 2 erreurs. Surtout, à 0,60, l'avis « Le design est joli mais… » (score 0,61) du jeu d'or devient une erreur franche : notre test `test_jeu_or.py` l'a détecté quand le kit du TP 2 a remis 0,60. Nous avons gardé 0,65 : un humain de plus à solliciter coûte moins cher qu'un client mécontent ignoré.
- **Limite de ce réglage :** le seuil a été choisi sur ces mêmes 58 avis ; une évaluation rigoureuse demanderait un jeu de validation séparé.

## 6. TP 2 : une API versionnée et protégée, et ses clients

- **Version `/v1` :** `/v1/health` (publique), `/v1/predict` (rôles client et admin) et `/v1/modele` (admin seulement : seuil et métriques). L'ancienne route `/predict` marche toujours, mais répond avec les en-têtes `Deprecation: true` et `Link: </v1/predict>` pour annoncer son remplacement.
- **Clés d'API et rôles :** la clé passe dans l'en-tête `X-API-Key` ; les clés et leur rôle sont lus dans `API_KEYS` (fichier `.env`, ignoré par Git). Une clé de moins de 16 caractères empêche l'API de démarrer, et la comparaison utilise `secrets.compare_digest` pour ne pas révéler la clé par le temps de réponse. Nous avons vérifié les cinq cas dans `/docs` (captures `docs/captures/tp2-c1-*.png`) : **401** sans clé (authentification), **200** avec la clé client, **422** pour un texte d'espaces, **403** pour `/v1/modele` en client (autorisation), et `seuil_abstention: 0.65` avec la clé admin.
- **Format d'erreur unique :** toutes les erreurs `/v1` ont la forme `{"erreur": {"code", "message", "champs"}}`. Les clients testent le **code**, stable (`NON_AUTHENTIFIE`, `ENTREE_INVALIDE`…), jamais le message.
- **Client web :** la page `web/` affiche le verdict, l'abstention (« à faire vérifier par un humain », 61 %) et une clé refusée (captures `tp2-c2-1` à `tp2-c2-3`).
- **Expérience CORS :** servie sur le port 5600 au lieu de 5500, la même page affiche « API injoignable ». La console montre que la **requête de pré-vérification** (`OPTIONS`) est refusée faute d'en-tête `Access-Control-Allow-Origin` (capture `tp2-c2-4-cors-port-5600.png`). CORS est une protection du navigateur : il ne remplace pas la clé, et `curl` ou Streamlit n'y sont pas soumis.
- **Service Java :** compilé et testé (5 tests JUnit) par la CI ; nous ne l'avons pas lancé sur nos postes, faute de Maven installé.

## 7. TP 3 : l'interface Streamlit et ses graphiques

- **Architecture découplée :** l'interface n'importe jamais le modèle ; elle appelle `/v1` avec la clé lue dans `.env` (`load_dotenv()`), car Streamlit ne lit pas ce fichier seul.
- **Un avis :** « Avis positif, 78 % » ; l'avis mitigé donne « Je ne sais pas : à faire vérifier par un humain, 61 % » avec un encadré qui explique l'abstention (captures `tp3-c2`, `tp3-c3`).
- **Un fichier :** `data/avis_exemple.csv` donne **2 positifs, 2 négatifs, 2 à vérifier** (mots inventés à 0,516 et « Pas déçu du tout » à 0,618). L'ancien résultat attendu (1/2/3) supposait un seuil de 0,60.
- **Deux graphiques :** la répartition des verdicts et la distribution de la confiance (captures `tp3-c5`, `tp3-c6`). Le code du manuel découpait les scores avec `pd.cut(bins=[0.5, 0.6, …])`, fermé à droite : un score de 0,5 n'entrait dans aucune tranche, et la frontière ne correspondait pas à notre seuil. Nous avons utilisé `bins=[0.5, 0.65, 0.7, 0.8, 0.9, 1.01]` avec `right=False` : la première tranche compte exactement les 2 abstentions. Ces graphiques résument les sorties du modèle ; sans étiquettes, ils ne mesurent pas sa justesse.
- **API arrêtée :** la page affiche « API injoignable » sans planter (capture `tp3-c7`) : l'affichage (port 8501) et le traitement (port 8000) sont deux programmes distincts.

## 8. TP 4 : le paquet 1.0.0 et sa release

- **Paquet :** `src/sentiment_app/`, version `1.0.0` écrite une seule fois dans `pyproject.toml` (lue par `importlib.metadata`). La commande `sentiment "texte"` accepte `--json` et `--version`, et renvoie le code de sortie 2 pour un texte vide.
- **Modèle embarqué :** la ligne `package-data` place `modele/*.joblib` dans la roue, et `importlib.resources` le retrouve où que le paquet soit installé. C'est le choix inverse de notre version 0.6.0, où le modèle restait à côté (`SENTIMENT_MODELE`). Embarquer le modèle rend la roue autonome, mais chaque nouveau modèle impose une nouvelle version du paquet. `scikit-learn` est figé en 1.5, car le fichier joblib n'est relisible qu'avec cette version.
- **Vérification :** `scripts/verifier_livrable.py` construit un environnement neuf, y installe la roue (9 695 octets), lance les 6 tests de `test_paquet.py` sur le paquet installé, puis la commande : **Bilan : CONFORME**, sous Windows avec Python 3.11.9.
- **Release :** l'étiquette `v1.0.0` désigne le commit `80f6e6b` ; la release joint la roue, l'archive source et le rapport. Depuis n'importe quel poste : `pip install https://github.com/ilyas701/sentiment-app/releases/download/v1.0.0/sentiment_app-1.0.0-py3-none-any.whl`, puis `sentiment "Livraison rapide, très satisfait"`, qui affiche `positive (confiance 77%)`.

## 9. Ce qui a échoué et résolution des blocages

1. **Chemins d'import** entre `src/`, `tests/`, `api/` et `ui/` (erreurs `ModuleNotFoundError`), résolus par `pythonpath` dans `pytest.ini` et l'ajout explicite de la racine à `sys.path`.
2. **Conflits de versions** (`pyarrow`, `numpy<2`), résolus en figeant les dépendances dans `requirements.txt`.
3. **Mauvais kit appliqué :** un ancien kit du TP 3, resté dans le dossier de travail, a écrasé `api/main.py` et `api/model.py`. Le commit du TP 2 nous a permis de tout restaurer avec `git restore .`.
4. **`pytest.ini` trop permissif :** avec `pythonpath = . src`, le test du paquet installé lisait les sources au lieu de la roue, et le vérificateur échouait. Nous avons gardé `pythonpath = .`.
5. **Ancien paquet encore installé :** la version 0.6.0, installée en mode éditable, aurait faussé les tests du nouveau paquet ; il a fallu la désinstaller (`pip uninstall`).
6. **Dossier vide non suivi :** Git ne garde pas un dossier vide ; sur un clone neuf, `src/sentiment_app/modele/` manquait. Un fichier `.gitkeep` le conserve.
7. **CI rouge après la fusion :** la CI installait `pytest` sans version, donc pytest 9, qui casse `test_lot_et_resume` (le modèle retiré par un test précédent n'était pas remis). Nous l'avons reproduit à l'identique, puis figé `pytest==8.3.*` comme dans `requirements.txt` : CI verte. Une dépendance non figée finit par casser.
8. **Étiquette déplacée :** la fusion avec un commit du binôme a créé un nouveau commit ; il a fallu déplacer `v1.0.0` (`git tag -f`) et revérifier, car le vérificateur exige l'étiquette sur le dernier commit.

## 10. Ce que nous ferions autrement

- Régler le seuil sur un jeu de validation distinct du jeu de test.
- Mettre en cache les appels par lot dans Streamlit (`@st.cache_data`).
- Surveiller la dérive des données et réinjecter les avis `INDETERMINE` étiquetés par les humains dans l'entraînement.
- Distribuer le modèle séparément de la roue (registre de modèles), pour le mettre à jour sans republier le paquet.
- Héberger l'interface : il faudrait aussi une API joignable depuis Internet, car le `localhost` d'un hébergeur n'est pas notre poste.

## 11. Réponses aux questions de bilan

1. **Où est le modèle ?** Pour l'API et Streamlit, dans `models/sentiment.joblib`, chargé par l'API au démarrage ; pour le paquet installé, à l'intérieur de la roue (`sentiment_app/modele/`).
2. **Un score élevé sur un avis mal classé ?** Le modèle est sûr de lui et se trompe : l'abstention ne rattrape pas ces erreurs confiantes, seules de meilleures données ou un meilleur modèle le peuvent.
3. **Pourquoi `INDETERMINE` n'est pas une erreur serveur ?** C'est une décision métier (le score est sous le seuil), renvoyée avec un statut 200 ; une erreur serveur (500, 503) signifie que le service n'a pas pu répondre.
4. **Prouver que la roue est autonome ?** L'installer dans un environnement neuf, hors des sources, et y lancer les tests et la commande : c'est ce que fait le vérificateur (CONFORME).
5. **Lancé, distribué, hébergé ?** L'API, Streamlit et le client web ont été **lancés en local** ; le paquet est **distribué** par la release GitHub ; rien n'est **hébergé** sur Internet.

## 12. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| Ilyas (@ilyas701) | Pipeline de modélisation, tests de qualité (ruff, mypy, pre-commit), API FastAPI, paquet et CLI, CI GitHub Actions ; intégration des TP 2 à 4 du programme (API `/v1`, interface `/v1`, paquet 1.0.0, release). |
| Othman (@Othm4n) | Cadrage initial, client HTTP et interface Streamlit, tests d'interface et du client, construction et essais de la roue hors dépôt, validation des métriques du TP 2 ; rédaction des comptes rendus. |

## Outils d'aide à la rédaction

Un assistant d'IA (Claude) a été utilisé pour intégrer les kits des TP 2 à 4, diagnostiquer des erreurs (dont l'échec de la CI avec pytest 9) et rédiger une première version de ce compte rendu. Les commandes, les tests, les captures et le vérificateur ont été exécutés sur nos postes, et les résultats chiffrés de ce document en proviennent.
