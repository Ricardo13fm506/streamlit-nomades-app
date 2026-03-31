import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime 
import json
import os

# Paramètres de configuration principaux de l’application Streamlit (titre, icône, largeur)
st.set_page_config(page_title="Nomades Mobile Analysis", layout="wide", page_icon="📱")

# Cette fonction charge les données du fichier Excel et les met en cache pour accélérer les chargements suivants.
@st.cache_data  # Le décorateur @st.cache_data permet de mettre en cache les données
def load_data():
    df = pd.read_excel('data/mobiles_suisse.xlsx')
    df = df.round(1)
    return df

# Cette fonction sauvegarde un nouveau commentaire dans un fichier JSON.
# Si le fichier existe, elle ajoute le commentaire ; sinon, elle crée la liste.
def save_comment(name, email, rating, comment):
    comments_file = 'data/comments.json'
    
    if os.path.exists(comments_file):
        with open(comments_file, 'r', encoding='utf-8') as f:
            comments = json.load(f)
    else:
        comments = []
    
    new_comment = {
        'name': name,
        'email': email,
        'rating': rating,
        'comment': comment,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    comments.append(new_comment)
    
    with open(comments_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    return True

# Cette fonction charge tous les commentaires enregistrés depuis le fichier JSON.
# Si le fichier n’existe pas, elle retourne une liste vide.
def load_comments():
    comments_file = 'data/comments.json'
    if os.path.exists(comments_file):
        with open(comments_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Cette fonction met en forme un DataFrame Pandas et colorie les scores.
# Les lignes de score élevées, moyennes ou faibles sont colorées différemment pour faciliter la lecture.
def style_dataframe(df):
    def highlight_scores(val):
        if pd.notna(val):  # Vérifie si la valeur existe (n’est ni vide ni NaN)
            try:
                num_val = float(val)
                if num_val >= 8:
                    return 'background-color: #90EE90'
                elif num_val >= 6:
                    return 'background-color: #FFD700'
                elif num_val < 5:
                    return 'background-color: #FFB6C1'
            except:
                pass
        return ''
    # Détecte les colonnes contenant des scores.
    score_cols = [col for col in df.columns if 'Score' in str(col) or 'score' in str(col).lower()]
    
    # Formate tous les scores à 1 décimale, comme des chaînes de caractères.
    for col in score_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else x)
    
    # Applique les couleurs définies ci-dessus
    styler = df.style.applymap(highlight_scores, subset=score_cols)
    
    return styler

# Cette fonction construit un dictionnaire associant chaque smartphone à ses scores et caractéristiques.
# Utile pour les comparaisons, graphiques et analyses détaillées dans l’application.
def get_smartphone_data_with_scores(df):
    smartphones = {}
    cols = list(df.columns)
    smartphone_map = []
    i = 0
    while i < len(cols):
        col = cols[i]
        if (col != 'CARACTÉRISTIQUES' and 
            'Score' not in col and 
            'score' not in col.lower() and
            '/10' not in col and
            '(/10)' not in col):
            score_col = None
            if i + 1 < len(cols):
                next_col = cols[i + 1]
                if ('Score' in next_col or 'score' in next_col.lower() or 
                    '/10' in next_col or '(/10)' in next_col):
                    score_col = next_col
            smartphone_map.append({
                'name': col,
                'score_col': score_col
            })
            i += 1
        else:
            i += 1
    for mapping in smartphone_map:
        phone_name = mapping['name']
        score_col = mapping['score_col']
        smartphones[phone_name] = {}
        for idx, row in df.iterrows():
            category = row['CARACTÉRISTIQUES']
            if pd.notna(category):
                if 'Score' in str(category):
                    if score_col and pd.notna(row[score_col]):
                        smartphones[phone_name][category] = row[score_col]
                    else:
                        smartphones[phone_name][category] = np.nan
                else:
                    smartphones[phone_name][category] = row[phone_name]
    return smartphones

def add_score_final_to_smartphones(smartphones_data, df):
    prix_row = df[df['CARACTÉRISTIQUES'] == 'Prix moyen']
    for phone in smartphones_data:
        try:
            scores = []
            for cat in [
                'Score Écran', 'Score Photo', 'Score Performance', 'Score Baterrie',
                'Score IA & LOGICIEL', 'Score MISES A JOUR', 'Score CONNECTIVITE'
            ]:
                val = smartphones_data[phone].get(cat)
                if pd.notna(val) and isinstance(val, (int, float, np.floating)):
                    scores.append(float(val))
            if not prix_row.empty and pd.notna(prix_row[phone].iloc[0]):
                price = float(prix_row[phone].iloc[0])
                if scores and price > 0:
                    score_final = round((np.mean(scores) / price) * 1000, 2)
                    smartphones_data[phone]['Score Final'] = score_final
                else:
                    smartphones_data[phone]['Score Final'] = None
        except Exception as e:
            smartphones_data[phone]['Score Final'] = None

# Fonction principale de l’application : initialise l’interface, charge les données et gère la navigation entre les pages.
def main():
    try:
        # Chargement des données; gestion des erreurs si le fichier est manquant ou au mauvais format
        df_horizontal = load_data()
    except FileNotFoundError:
        st.error("Error: File 'data/mobiles_suisse.xlsx' not found!")
        st.info("Make sure the Excel file is in the 'data/' folder with the correct name.")
        return
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Check if the Excel file is in the correct format")
        return
    
    # Menu latéral de navigation pour accéder aux différentes pages de l’application.
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "Home",
        "Comparison Table",
        "Graphics & Analysis",
        "Rankings",
        "Side-by-Side Comparison",
        "Comments"
    ])
    
    # Bloc d’accueil : introduction et résumé global du projet, statistiques principales
    if page == "Home":
        st.title("Nomades Mobile Analysis")
        st.markdown("**Detailed smartphone comparison** | Swiss Market 2025")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        # Calcul du nombre total de smartphones dans le tableau
        smartphone_cols = [col for col in df_horizontal.columns 
                          if col != 'CARACTÉRISTIQUES' 
                          and 'Score' not in col 
                          and 'score' not in col.lower()
                          and '/10' not in col
                          and '(/10)' not in col]
        with col1:
            st.metric("Total Smartphones", len(smartphone_cols))
        with col2:
            # Calcul du prix moyen parmi tous les smartphones
            prix_rows = df_horizontal[df_horizontal['CARACTÉRISTIQUES'] == 'Prix moyen']
            if not prix_rows.empty:
                prices = []
                for col in smartphone_cols:
                    val = prix_rows[col].iloc[0]
                    if pd.notna(val):
                        try:
                            if isinstance(val, (int, float)):
                                prices.append(float(val))
                            else:
                                price_str = str(val).replace('CHF', '').replace('€', '').replace("'", '').replace(' ', '').strip()
                                price = float(price_str)
                                prices.append(price)
                        except:
                            pass
                if prices:
                    st.metric("Average Price", f"CHF {np.mean(prices):.0f}")
                else:
                    st.metric("Average Price", "N/A")
            else:
                st.metric("Average Price", "N/A")
        with col3:
            # Heure du nombre total de catégories/critères techniques
            categories = df_horizontal['CARACTÉRISTIQUES'].dropna().tolist()
            st.metric("Total Categories", len(categories))
        st.markdown("---")
        # Explications des fonctionnalités de l’outil
        st.markdown("### Welcome to Nomades Mobile Analysis")
        st.markdown("This comprehensive tool allows you to:")
        st.markdown("- Compare 9 top smartphones in the Swiss market")
        st.markdown("- Analyze detailed specifications across 52 categories")
        st.markdown("- View interactive charts and rankings")
        st.markdown("- Make side-by-side comparisons")
        st.markdown("- Share your opinions in the comments section")
        st.markdown("**Use the navigation menu on the left to explore!**")
         # Page de tableau comparatif : sélection des catégories, options d’affichage et filtrage des données
    elif page == "Comparison Table":
        st.title("Comparison Table")
        st.markdown("---")
        st.sidebar.header("Filters")
        categories = df_horizontal['CARACTÉRISTIQUES'].dropna().tolist() 
        st.sidebar.subheader("Select Categories to Display")
        category_groups = {
            "General": ["Marque", "Modèle", "Prix", "Année"],
            "Display": ["Écran", "ÉCRAN", "Taille", "Résolution", "Technologie", "Type de dalle", "Taux de rafraîchissement", "Luminosité", "Protection"],
            "Performance": ["Processeur", "RAM", "Stockage", "Batterie", "Capacité"],
            "Camera": ["Appareil photo", "PHOTO", "VIDÉO", "Caméra", "Photo", "Vidéo", "Capteur", "Téléobjectif", "Ultra grand-angle", "Zoom"],
            "Features": ["Système", "5G", "NFC", "Charge", "Étanche", "IP", "Connectivité"]
        }
        selected_categories = []
        select_all = st.sidebar.checkbox("Select All Categories", value=True)
        if select_all:
            selected_categories = categories
        else:
            for group_name, keywords in category_groups.items():
                with st.sidebar.expander(group_name):
                    for category in categories:
                        is_in_group = any(keyword.lower() in category.lower() for keyword in keywords)
                        if is_in_group:
                            if st.checkbox(category, value=False, key=f"table_{category}"):
                                selected_categories.append(category)
        st.sidebar.markdown("---")
        st.sidebar.subheader("Display Options")
        highlight_scores = st.sidebar.checkbox("Highlight Scores", value=True)
        smartphones_only = st.sidebar.checkbox("Smartphones Only", value=False)
        if selected_categories:
            df_display = df_horizontal[df_horizontal['CARACTÉRISTIQUES'].isin(selected_categories)].copy()
        else:
            df_display = df_horizontal.copy()
        if smartphones_only and not df_display.empty:
            cols_to_keep = ['CARACTÉRISTIQUES']
            for col in df_display.columns:
                if col != 'CARACTÉRISTIQUES' and 'Score' not in str(col) and 'score' not in str(col).lower():
                    cols_to_keep.append(col)
            df_display = df_display[cols_to_keep]
        df_display = df_display.fillna("")
        if not df_display.empty:
            if highlight_scores:
                styled_df = style_dataframe(df_display)
                st.write(styled_df)
            else:
                st.dataframe(df_display, use_container_width=True, height=600, hide_index=True)
        else:
            st.warning("No category selected. Please select at least one category in the filters.")

    # Page d’analyses graphiques et radar : comparaison des scores, graphiques interactifs
    elif page == "Graphics & Analysis":
        st.title("Graphics & Analysis")
        st.markdown("---")
        smartphones_data = get_smartphone_data_with_scores(df_horizontal)
        add_score_final_to_smartphones(smartphones_data, df_horizontal)
        smartphone_names = list(smartphones_data.keys())
        st.subheader("Overall Score Comparison")
        score_categories = [
            'Score Écran',
            'Score Photo',
            'Score Performance',
            'Score Baterrie',
            'Score IA & LOGICIEL',
            'Score MISES A JOUR',
            'Score CONNECTIVITE',
            'Score Final'
        ]
        score_categories = [cat for cat in score_categories if cat in df_horizontal['CARACTÉRISTIQUES'].values]
        if score_categories:
            avg_scores = {}
            for phone in smartphone_names:
                scores = []
                for cat in score_categories:
                    if cat == 'Score Final':
                        continue
                    val = smartphones_data[phone].get(cat)
                    if pd.notna(val):
                        try:
                            score_val = float(val)
                            if score_val > 0:
                                scores.append(score_val)
                        except:
                            pass
                if scores:
                    avg_scores[phone] = np.mean(scores)
            if avg_scores:
                fig = go.Figure(data=[
                    go.Bar(x=list(avg_scores.keys()), y=list(avg_scores.values()),
                        marker_color='lightblue',
                        text=[f"{v:.2f}" for v in avg_scores.values()],
                        textposition='auto')
                ])
                fig.update_layout(
                    title="Average Score by Smartphone",
                    xaxis_title="Smartphone",
                    yaxis_title="Average Score (out of 10)",
                    height=500,
                    yaxis=dict(range=[0, 10])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No score data available.")
        st.markdown("---")
        st.subheader("Multi-dimensional Comparison (Radar Chart)")
        selected_phones_radar = st.multiselect(
            "Select smartphones to compare (max 3)", 
            smartphone_names, 
            default=smartphone_names[:min(3, len(smartphone_names))]
        )
        radar_score_options = [cat for cat in score_categories if cat != 'Score Final'][:7]
        radar_categories = st.multiselect(
            "Select categories for radar", 
            radar_score_options,
            default=radar_score_options[:min(5, len(radar_score_options))]
        )
          # Affichage du radar : génération d’un radar chart interactif selon la sélection utilisateur
        if selected_phones_radar and radar_categories:
            fig = go.Figure()
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
            for idx, phone in enumerate(selected_phones_radar):
                values = []
                for cat in radar_categories:
                    val = smartphones_data[phone].get(cat)
                    if pd.notna(val):
                        try:
                            score_val = float(val)
                            values.append(score_val)
                        except:
                            values.append(0)
                    else:
                        values.append(0)
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_categories,
                    fill='toself',
                    name=phone,
                    line=dict(color=colors[idx % len(colors)])
                ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 10],
                        tickfont=dict(size=10)
                    )
                ),
                showlegend=True,
                height=600,
                title="Multi-dimensional Score Comparison"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select smartphones and categories to display the radar chart.")

        st.markdown("---")
        # Affichage du graphique de distribution des prix par smartphone
        st.subheader("Price Distribution")
        prix_rows = df_horizontal[df_horizontal['CARACTÉRISTIQUES'] == 'Prix moyen']
        if not prix_rows.empty:
            price_data = {}
            for col in smartphone_names:
                val = prix_rows[col].iloc[0]
                if pd.notna(val):
                    try:
                        if isinstance(val, (int, float)):
                            price = float(val)
                        else:
                            price_str = str(val).replace('CHF', '').replace('€', '').replace("'", '').replace(' ', '').strip()
                            price = float(price_str)
                        if price > 0:
                            price_data[col] = price
                    except:
                        pass
            if price_data:
                fig = go.Figure(data=[go.Pie(
                    labels=list(price_data.keys()),
                    values=list(price_data.values()),
                    hole=.3,
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig.update_layout(title="Price Distribution by Smartphone", height=500)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        # Affichage du nuage de points ("scatter") : analyse de la corrélation Prix vs Performance
        st.subheader("Price vs Performance Analysis")
        if not prix_rows.empty and score_categories:
            scatter_data = []
            for phone in smartphone_names:
                price = None
                val = prix_rows[phone].iloc[0]
                if pd.notna(val):
                    try:
                        if isinstance(val, (int, float)):
                            price = float(val)
                        else:
                            price_str = str(val).replace('CHF', '').replace('€', '').replace("'", '').replace(' ', '').strip()
                            price = float(price_str)
                    except:
                        pass
                scores = []
                for cat in score_categories:
                    if cat == 'Score Final':
                        continue
                    val = smartphones_data[phone].get(cat)
                    if pd.notna(val):
                        try:
                            score_val = float(val)
                            if score_val > 0:
                                scores.append(score_val)
                        except:
                            pass
                if price and price > 0 and scores:
                    avg_score = np.mean(scores)
                    scatter_data.append({'Phone': phone, 'Price': price, 'Performance': avg_score})
            if scatter_data:
                df_scatter = pd.DataFrame(scatter_data)
                fig = px.scatter(
                    df_scatter, 
                    x='Price', 
                    y='Performance', 
                    text='Phone',
                    size='Performance', 
                    color='Performance',
                    color_continuous_scale='Viridis',
                    size_max=20
                )
                fig.update_traces(textposition='top center', textfont_size=10)
                fig.update_layout(
                    height=500, 
                    title="Price vs Performance Analysis",
                    xaxis_title="Price (CHF)",
                    yaxis_title="Average Performance Score",
                    yaxis=dict(range=[0, 10])
                )
                st.plotly_chart(fig, use_container_width=True)

    # Page des classements: calcul et affichage du top 3, classement général et filtres par catégorie
    elif page == "Rankings":
        st.title("Rankings")
        st.markdown("---")
        smartphones_data = get_smartphone_data_with_scores(df_horizontal)
        add_score_final_to_smartphones(smartphones_data, df_horizontal)
        smartphone_names = list(smartphones_data.keys())
        st.subheader("Top 3 Smartphones - Overall Score")
        score_categories = [
            'Score Écran',
            'Score Photo',
            'Score Performance',
            'Score Baterrie',
            'Score IA & LOGICIEL',
            'Score MISES A JOUR',
            'Score CONNECTIVITE'
        ]
        score_categories = [cat for cat in score_categories if cat in df_horizontal['CARACTÉRISTIQUES'].values]
        if score_categories:
            avg_scores = {}
            for phone in smartphone_names:
                scores = []
                for cat in score_categories:
                    val = smartphones_data[phone].get(cat)
                    if pd.notna(val):
                        try:
                            score_val = float(val)
                            if score_val > 0:
                                scores.append(score_val)
                        except:
                            pass
                if scores:
                    avg_scores[phone] = np.mean(scores)
            if avg_scores:
                sorted_phones = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
                col1, col2, col3 = st.columns(3)
                if len(sorted_phones) >= 1:
                    with col1:
                        st.metric("🥇 1st Place", sorted_phones[0][0], f"{sorted_phones[0][1]:.2f}/10")
                if len(sorted_phones) >= 2:
                    with col2:
                        st.metric("🥈 2nd Place", sorted_phones[1][0], f"{sorted_phones[1][1]:.2f}/10")
                if len(sorted_phones) >= 3:
                    with col3:
                        st.metric("🥉 3rd Place", sorted_phones[2][0], f"{sorted_phones[2][1]:.2f}/10")
                st.markdown("---")
                st.subheader("Complete Ranking")
                for i, (phone, score) in enumerate(sorted_phones, 1):
                    st.write(f"**{i}.** {phone}: **{score:.2f}/10**")
            else:
                st.warning("No score data available for ranking.")
        st.markdown("---")
        # Meilleur smartphone pour chaque catégorie (classement par score d’une catégorie choisie)
        st.subheader("Best Smartphone by Category")
        category_select = st.selectbox("Select a category", score_categories if score_categories else [])
        if category_select:
            category_scores = {}
            for phone in smartphone_names:
                val = smartphones_data[phone].get(category_select)
                if pd.notna(val):
                    try:
                        score_val = float(val)
                        if score_val > 0:
                            category_scores[phone] = score_val
                    except:
                        pass
            if category_scores:
                sorted_category = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                st.write(f"**Top 5 for {category_select}:**")
                for i, (phone, score) in enumerate(sorted_category[:5], 1):
                    medal = ""
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    st.write(f"{medal} **{i}. {phone}**: {score}/10")
            else:
                st.warning(f"No data available for {category_select}")
        st.markdown("---")
        # Meilleur rapport qualité/prix (Valeur Score)
        st.subheader("Best Value for Money")
        prix_rows = df_horizontal[df_horizontal['CARACTÉRISTIQUES'] == 'Prix moyen']
        if not prix_rows.empty and score_categories:
            value_scores = {}
            for phone in smartphone_names:
                price = None
                try:
                    val = prix_rows[phone].iloc[0]
                    if pd.notna(val):
                        if isinstance(val, (int, float)):
                            price = float(val)
                        else:
                            price_str = str(val).replace('CHF', '').replace('€', '').replace("'", '').replace(' ', '').strip()
                            price = float(price_str)
                except:
                    pass
                scores = []
                for cat in score_categories:
                    val = smartphones_data[phone].get(cat)
                    if pd.notna(val):
                        try:
                            score_val = float(val)
                            if score_val > 0:
                                scores.append(score_val)
                        except:
                            pass
                if price and price > 0 and scores:
                    avg_score = np.mean(scores)
                    value_scores[phone] = (avg_score / price) * 1000
            if value_scores:
                sorted_value = sorted(value_scores.items(), key=lambda x: x[1], reverse=True)
                st.write("**Top 5 Value for Money:**")
                st.info("Value Score = (Average Score / Price) × 1000")
                for i, (phone, value) in enumerate(sorted_value[:5], 1):
                    medal = ""
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    st.write(f"{medal} **{i}. {phone}**: Value Score {value:.2f}")
            else:
                st.warning("Not enough data to calculate value for money.")
        else:
            st.warning("Price or score data not available.")

    # Comparaison côte à côte de deux smartphones (toutes les caractéristiques/catégories cote à cote)
    elif page == "Side-by-Side Comparison":
        st.title("Side-by-Side Comparison")
        st.markdown("---")
        .\.venv\Scripts\activate get_smartphone_data_with_scores(df_horizontal)
        add_score_final_to_smartphones(smartphones_data, df_horizontal)
        smartphone_names = list(smartphones_data.keys())
        col1, col2 = st.columns(2)
        with col1:
            phone1 = st.selectbox("Select first smartphone", smartphone_names, key="phone1")
        with col2:
            available_phones = [p for p in smartphone_names if p != phone1]
            phone2 = st.selectbox("Select second smartphone", available_phones, key="phone2")
        if phone1 and phone2:
            st.markdown("---")
            categories = df_horizontal['CARACTÉRISTIQUES'].dropna().tolist()
            comparison_data = []
            for cat in categories:
                val1 = smartphones_data[phone1].get(cat, "N/A")
                val2 = smartphones_data[phone2].get(cat, "N/A")
                if pd.isna(val1):
                    val1 = "N/A"
                if pd.isna(val2):
                    val2 = "N/A"
                comparison_data.append({
                    'Category': cat,
                    phone1: val1,
                    phone2: val2
                })
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, height=600, hide_index=True)

    # Système de commentaires et avis utilisateurs : formulaire et affichage des commentaires récents.
    elif page == "Comments":
        st.title("Comments & Reviews")
        st.markdown("---")
        st.subheader("Leave your opinion")
        with st.form("comment_form"):
            name = st.text_input("Name *", placeholder="Your name")
            email = st.text_input("Email (optional)", placeholder="your@email.com")
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Your comment *", placeholder="Share your thoughts about the smartphones...", height=150)
            submitted = st.form_submit_button("Submit Comment")
            if submitted:
                if name and comment:
                    if save_comment(name, email, rating, comment):
                        st.success("Thank you! Your comment has been posted!")
                        st.rerun()
                else:
                    st.error("Please fill in all required fields (Name and Comment)")
        st.markdown("---")
        st.subheader("Recent Comments")
        comments = load_comments()
        if comments:
            for c in reversed(comments[-10:]):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{c['name']}**")
                        st.markdown(f"{'⭐' * c['rating']}")
                    with col2:
                        st.markdown(f"*{c['date']}*")
                    st.markdown(f"{c['comment']}")
                    st.markdown("---")
        else:
            st.info("No comments yet. Be the first to comment!")

    # Pied de page de l’application
    st.markdown("---")
    st.markdown("**Nomades Mobile Analysis** | Detailed smartphone comparison | 2025")

# Point d’entrée principal du script Streamlit : lance l’app.
if __name__ == "__main__":
    main()