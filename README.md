Analyse interactive et comparaison avancée de smartphones sur le marché suisse

Description:

Ce projet est une application interactive construite avec Streamlit, permettant de comparer, analyser et visualiser les caractéristiques et performances des principaux smartphones disponibles en Suisse. L'outil offre des tableaux, graphiques, classements et fonctionnalités de commentaires pour faciliter la prise de décision

Fonctionnalités:

Tableau comparatif : comparaison détaillée entre plusieurs modèles et catégories techniques. Analyse graphique : graphiques interactifs (barres, radar, camembert, scatter) pour explorer les tendances de scores et prix. Classements : meilleurs modèles par score général, catégorie, et rapport qualité/prix. Comparaison côte-à-côte : examiner deux smartphones en parallèle, catégorie par catégorie. Section commentaires : possibilité de laisser un avis ou lire ceux d’autres utilisateurs. Filtres avancés : sélection dynamique des catégories et options d'affichage. Codes couleur pour les scores : compréhension visuelle immédiate (vert = excellent, jaune = bon, rose = faible).

Calcul du Score Final :

L’application utilise une fonction spécifique (add_score_final_to_smartphones) pour calculer un Score Final permettant de comparer la performance globale de chaque smartphone, ajustée à son prix.

Pour chaque smartphone, la fonction récupère les scores techniques disponibles : Score Écran, Score Photo, Score Performance, Score Batterie, Score IA & Logiciel, Score Mises à Jour, Score Connectivité. La moyenne de ces scores est calculée, en ignorant les valeurs manquantes. Le prix moyen ("Prix moyen") est extrait du fichier de données. Le Score Final est calculé selon la formule suivante : Score Final = (moyenne des scores / prix) × 1000. Ce score met en valeur la performance par rapport au prix et facilite la comparaison qualitative et quantitative.

Pour ajouter un nouveau smartphone, il suffit d’analyser la fiche technique du modèle, de compléter dans le fichier de données (mobiles_suisse.xlsx) une ligne pour ce modèle avec les scores pour chaque catégorie ainsi que son prix moyen, puis d’enregistrer et relancer l’application. La fonction calculera automatiquement le Score Final pour ce modèle sans besoin de modifier le code. Si certaines catégories n’ont pas de valeur, elles seront simplement ignorées dans le calcul de la moyenne.

Installation et Lancement

Cloner ce dépôt :

git clone https://github.com/Ricardo13fm506/streamlit-nomades-app.git cd streamlit-nomades-app

Installer les dépendances :

pip install -r requirements.txt

Placer le fichier de données mobiles_suisse.xlsx dans le dossier data/ (voir exemples ou demandez un extrait si besoin).

Lancer l’application :

streamlit run nomades_mobile_analysis.py

Structure de l’application:

Home : présentation générale et statistiques globales. Comparison Table : tableau personnalisable avec filtres. Graphics & Analysis : visualisation dynamique des scores, radar, analyse prix/performance. Rankings : classements (top scores, catégories, meilleur rapport qualité/prix). Side-by-Side Comparison : comparaison détaillée de deux smartphones choisis. Comments : espace participatif pour avis utilisateurs.

Technologies utilisées Python 3 Streamlit (front-end interactif) Pandas (traitement de données) Plotly (visualisation de graphiques) Openpyxl (lecture des fichiers Excel) Numpy (traitement mathématique et statistique)

Développement futur (suggestions):

Ajout de statistiques « meilleures ventes » ou parts de marché (si données disponibles) Téléchargement/export PDF ou Excel de comparaisons Authentification utilisateur et profils personnalisés Support multilingue (fr, en, pt) Ajout d’images pour chaque smartphone Intégration d’API de prix ou d'avis extérieurs

Auteur: Développé par Ricardo13fm506 pour Nomades Advanced Technologies


