import streamlit as st
import requests
import datetime
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import urllib.parse
import pandas as pd
import numpy as np
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt
import urllib.parse
from streamlit_extras.sandbox import sandbox
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit import expander

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbws-rrMtZKiCSBTTg7pfVuDH93LcOM-RrDRayAerWsgMVVLPCOZGvP1fND6mcvZEI2oWg/exec"

st.set_page_config(
    page_title="Dashboard Client",
    page_icon="📊",
    layout="wide",      # Layout large
    initial_sidebar_state="expanded"
)
def get_clients():
    try:
        response = requests.get(WEBHOOK_URL, params={"action": "get_clients"})
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erreur lors de la récupération des clients.")
            return []
    except Exception as e:
        st.error(f"Erreur réseau : {e}")
        return []

def find_client(clients, prenom, nom, dob):
    dob_str = dob.strftime("%Y-%m-%d")
    for c in clients:
        if (c.get("prenom","").strip().lower() == prenom.strip().lower() and
            c.get("nom","").strip().lower() == nom.strip().lower() and
            c.get("dob","") == dob_str):
            return c
    return None
def show_dashboard(client):
    st.title(f"📊 Dashboard")

    # Définir les onglets
    tab1, tab3, tab4, tab5 = st.tabs([
        "👤 Infos personnelles",
        "🗒️ Suivi personnalisé ",
        "➕ Nouveau feedback",
        "⚖️ Score & IMC"
    ])

    def example():
        col1, col2, col3 = st.columns(3)

        col1.metric(label="Gain", value=5000, delta=1000)
        col2.metric(label="Loss", value=5000, delta=-1000)
        col3.metric(label="No Change", value=5000, delta=0)

        style_metric_cards()

    with tab1:

        # 🔑 Données simulées du client
        client = {
            "email": "client@example.com",
            "telephone": "+33 6 12 34 56 78",
            "niveau": "Intermédiaire",
            "objectif": "Perte de poids",
            "remarques": "A suivre de près",
            "poids": 70,
            "taille": 175,
            "dob": "1995-06-15",
            "poids_cible": 65
        }

        # ---------------------------
        # 📂 Informations personnelles
        with st.expander("ℹ️ Détails personnels", expanded=False):
            st.header("👤 Profil client")
            infos = {
                "📧 Email": client["email"],
                "📞 Téléphone": client["telephone"],
                "🏋️ Niveau sportif": client["niveau"],
                "🎯 Objectif": client["objectif"],
                "📝 Remarques": client["remarques"],
                "⚖️ Poids (kg)": client["poids"],
                "📏 Taille (cm)": client["taille"],
                "🎂 Date de naissance": client["dob"]
            }
            col1, col2 = st.columns(2)
            for idx, (key, val) in enumerate(infos.items()):
                with (col1 if idx % 2 == 0 else col2):
                    st.write(f"**{key}** : {val}")

        # ---------------------------
        # 📊 Données de suivi
        st.subheader("📊 Évolution du poids et de l’IMC")

        nb_points = 20
        dates = [datetime.date.today() - datetime.timedelta(weeks=i) for i in reversed(range(nb_points))]
        taille_m = client["taille"] / 100
        poids = [client["poids"] - (nb_points - i) * 0.2 + np.random.normal(0, 0.3) for i in range(nb_points)]
        imc = [p / taille_m ** 2 for p in poids]

        df = pd.DataFrame({
            "Date": dates,
            "Poids (kg)": poids,
            "IMC": imc
        })

        # 📈 Graphiques Altair
        def make_chart(title, y_label, y_data, color):
            return alt.Chart(df).mark_line(point=True, color=color).encode(
                x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%d %b")),
                y=alt.Y(f"{y_label}:Q", title=y_label),
                tooltip=["Date:T", f"{y_label}:Q"]
            ).properties(title=title, width=350, height=300).interactive()

        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(make_chart("📉 Courbe du Poids", "Poids (kg)", "Poids (kg)", "steelblue"),
                            use_container_width=True)
        with col2:
            st.altair_chart(make_chart("📈 Courbe de l’IMC", "IMC", "IMC", "orange"), use_container_width=True)

        # ---------------------------
        # 📏 Écart au poids cible
        st.subheader("📉 Écart au poids cible")

        ecart_df = df.copy()
        ecart_df["Objectif"] = client["poids_cible"]
        ecart_df["Écart"] = ecart_df["Poids (kg)"] - client["poids_cible"]

        chart_ecart = alt.Chart(ecart_df).mark_bar(color='orangered').encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Écart:Q", title="Écart (kg)"),
            tooltip=["Date:T", "Poids (kg):Q", "Écart:Q"]
        ).properties(
            title="🎯 Écart entre poids mesuré et objectif",
            width=700, height=400
        )

        st.altair_chart(chart_ecart, use_container_width=True)

        # ---------------------------
        # 📌 Indicateurs clés
        st.subheader("📌 Indicateurs clés")

        col1, col2, col3, col4 = st.columns(4)

        poids_actuel = poids[-1]
        imc_actuel = imc[-1]
        ecart = poids_actuel - client["poids_cible"]

        with col1:
            st.metric("Poids actuel (kg)", f"{poids_actuel:.1f}", f"{poids_actuel - poids[-2]:+.1f} kg", border = True)
        with col2:
            st.metric("IMC actuel", f"{imc_actuel:.1f}", f"{imc_actuel - imc[-2]:+.1f}", border = True)
        with col3:
            st.metric("Écart objectif (kg)", f"{ecart:.1f}", f"{ecart:+.1f}", border = True)
        with col4:
            st.metric("Séances totales", "29", "+2", border = True)

        # ---------------------------
        # 📈 Progression vers l’objectif
        st.subheader("🎯 Progression vers l’objectif de poids")

        progress = (client["poids"] - poids_actuel) / (client["poids"] - client["poids_cible"])
        st.progress(min(max(progress, 0), 1))

        # ---------------------------
        # ❤️ Score santé global (fictif)
        st.subheader("💡 Score de santé (simulation)")
        score_sante = np.random.randint(60, 90)
        st.success(f"Score : {score_sante}/100")
        st.caption("Ce score est une simulation basée sur les données récentes.")

    with tab3:
        st.subheader("🔗 Envie d’avancer avec un coach qualifié ?")
        st.markdown("""
        Vous souhaitez être accompagné par un coach professionnel pour atteindre vos objectifs ?
        Remplissez le formulaire ci-dessous et nous vous mettrons en relation avec le coach le plus adapté à vos besoins.
        """)

        with st.form("coach_contact_form"):
            st.write("Remplissez ce formulaire pour être contacté par un coach :")
            name = st.text_input("👤 Votre prénom et nom", placeholder="Jean Dupont")
            email = st.text_input("📧 Votre adresse email", placeholder="jeandupont@email.com")
            phone = st.text_input("📞 Votre numéro de téléphone (optionnel)", placeholder="0612345678")

            objectif_options = [
                "Perte de poids",
                "Prise de masse",
                "Remise en forme",
                "Préparation sportive",
                "Autre"
            ]
            objectif = st.selectbox("🎯 Quel est votre objectif principal ?", objectif_options)

            if objectif == "Autre":
                objectif = st.text_area("🎯 Parlez-nous de vos objectifs spécifiques")

            dispo_options = [
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi",
                "Samedi",
                "Dimanche"
            ]
            dispo_days = st.multiselect("🗓️ Quels jours êtes-vous disponible ?", dispo_options)
            dispo_time = st.text_input("🕒 À quelles heures êtes-vous disponible ?", placeholder="Ex: 18h-20h")

            preferences = st.text_area("💡 Avez-vous des préférences ou des besoins spécifiques ?",
                                       placeholder="Ex: Coach spécialisé en nutrition, séances à domicile, etc.")

            submit = st.form_submit_button("📩 Je souhaite être contacté")

            if submit:
                if name and email and objectif:
                    st.success("Merci ! Un coach vous contactera sous peu. 💪")
                else:
                    st.warning("Merci de remplir tous les champs obligatoires.")

        st.markdown("---")
        st.subheader("📢 Partagez avec vos amis")
        st.markdown("""
        Vous pensez que ce service pourrait intéresser vos amis ? Partagez-le sur les réseaux sociaux !
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("[![Facebook](https://img.icons8.com/color/48/000000/facebook.png)](https://www.facebook.com)")
        with col2:
            st.markdown("[![Twitter](https://img.icons8.com/color/48/000000/twitter.png)](https://www.twitter.com)")
        with col3:
            st.markdown(
                "[![Instagram](https://img.icons8.com/color/48/000000/instagram-new.png)](https://www.instagram.com)")

        st.markdown("---")
        st.subheader("❓ FAQ")
        st.markdown("""
        **Comment se déroule la mise en relation avec un coach ?**
        Une fois que vous avez rempli le formulaire, nous analysons vos besoins et vous mettons en relation avec le coach le plus adapté. Vous serez contacté sous 48 heures.

        **Quels sont les tarifs des coachs ?**
        Les tarifs varient en fonction des coachs et de vos besoins spécifiques. Vous recevrez une proposition détaillée lors de la mise en relation.

        **Puis-je changer de coach si je ne suis pas satisfait ?**
        Oui, nous nous engageons à vous trouver le coach qui vous convient le mieux. Si vous n'êtes pas satisfait, nous ferons le nécessaire pour vous proposer une alternative.
        """)

    # --- Onglet 4 : Ajouter un nouveau feedback ---
    with tab4:
        st.header("➕ Ajouter un nouveau feedback")
        nouveau_feedback = st.text_area("Rédigez votre feedback ci-dessous :")
        if st.button("Envoyer le feedback"):
            if nouveau_feedback.strip():
                # Ici, tu pourras ajouter l'appel à ton backend
                st.success("✅ Merci pour votre feedback ! (à implémenter dans le backend)")
            else:
                st.warning("❗ Veuillez entrer un feedback avant d'envoyer.")

    # --- Onglet 5 : Score & IMC ---


    with tab5:
        # Titre
        st.subheader("💪 Évalue ton score santé de façon complète et dynamique")

        # Collecte des données
        st.subheader("📋 Tes informations personnelles")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Informations physiques**")
            poids = st.number_input("Poids (kg)", 20.0, 300.0, 70.0, help="Entrez votre poids en kilogrammes.")
            taille_cm = st.number_input("Taille (cm)", 100.0, 250.0, 170.0, help="Entrez votre taille en centimètres.")
            tour_taille = st.number_input("Tour de taille (cm)", 40.0, 200.0, 80.0,
                                          help="Entrez votre tour de taille en centimètres.")
            age = st.number_input("Âge", 10, 120, 30, help="Entrez votre âge en années.")
            genre = st.selectbox("Genre", ["Homme", "Femme"], help="Sélectionnez votre genre.")

            st.markdown("**Habitudes de vie**")
            fumeur = st.selectbox("Fumeur ?", ["Non", "Occasionnel", "Régulier"],
                                  help="Sélectionnez votre habitude tabagique.")
            alcool = st.selectbox("Consommation d'alcool ?", ["Jamais", "Rarement", "Souvent"],
                                  help="Sélectionnez votre fréquence de consommation d'alcool.")
            stress = st.slider("Niveau de stress", 0, 10, 5,
                               help="Évaluez votre niveau de stress sur une échelle de 0 à 10.")

        with col2:
            st.markdown("**Activité physique**")
            niveau_sportif = st.selectbox("Niveau sportif", ["Débutant", "Intermédiaire", "Avancé"],
                                          help="Sélectionnez votre niveau sportif.")
            activite_hebdo = st.slider("Heures de sport par semaine", 0, 20, 3,
                                       help="Entrez le nombre d'heures de sport que vous faites par semaine.")

            st.markdown("**Habitudes de sommeil et d'alimentation**")
            sommeil = st.slider("Heures de sommeil par nuit", 3, 12, 7,
                                help="Entrez le nombre d'heures de sommeil que vous avez par nuit.")
            alimentation = st.selectbox("Qualité de l'alimentation",
                                        ["Peu équilibrée", "Correcte", "Bonne", "Excellente"],
                                        help="Évaluez la qualité de votre alimentation.")
            repas_jour = st.slider("Nombre de repas par jour", 1, 6, 3,
                                   help="Entrez le nombre de repas que vous prenez par jour.")
            ant_fam = st.selectbox("Antécédents familiaux de maladies graves ?", ["Non", "Oui"],
                                   help="Avez-vous des antécédents familiaux de maladies graves ?")

        # Calculs
        taille_m = taille_cm / 100
        imc = poids / (taille_m ** 2)

        # Score
        score = 100

        # IMC
        if imc < 18.5 or imc > 25:
            score -= 15

        # Tour de taille
        if genre == "Homme":
            if tour_taille > 102:
                score -= 20
            elif tour_taille > 94:
                score -= 10
        else:
            if tour_taille > 88:
                score -= 20
            elif tour_taille > 80:
                score -= 10

        # Activité & sport
        if niveau_sportif == "Intermédiaire":
            score += 10
        elif niveau_sportif == "Avancé":
            score += 20
        if activite_hebdo >= 5:
            score += 10

        # Sommeil
        if sommeil >= 7:
            score += 5
        elif sommeil < 6:
            score -= 5

        # Alimentation
        if alimentation == "Bonne":
            score += 5
        elif alimentation == "Excellente":
            score += 10

        # Tabac & alcool
        if fumeur == "Occasionnel":
            score -= 5
        elif fumeur == "Régulier":
            score -= 15
        if alcool == "Souvent":
            score -= 10

        # Stress
        if stress >= 7:
            score -= 10

        # Repas déséquilibrés
        if repas_jour < 3:
            score -= 5

        # Antécédents familiaux
        if ant_fam == "Oui":
            score -= 5

        # Age bonus
        if age < 30:
            score += 5

        # Bornage
        score = max(0, min(score, 100))

        # Affichage score
        st.subheader(f"📊 **Score santé : {score} / 100**")

        # Jauge visuelle avec Plotly
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            title={'text': "Score Santé Global", 'font': {'size': 24}},
            delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "green" if score >= 80 else "orange" if score >= 60 else "red"},
                'steps': [
                    {'range': [0, 60], 'color': "#FF6666"},
                    {'range': [60, 80], 'color': "#FFCC66"},
                    {'range': [80, 100], 'color': "#66FF66"}
                ],
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Badge de niveau santé
        if score < 60:
            badge = "🥉 Bronze"
            next_level = "Argent"
            points_needed = 60 - score
        elif score < 80:
            badge = "🥈 Argent"
            next_level = "Or"
            points_needed = 80 - score
        elif score < 95:
            badge = "🥇 Or"
            next_level = "Platine"
            points_needed = 95 - score
        else:
            badge = "🏆 Platine"
            next_level = None
            points_needed = 0

        st.subheader(f"🏅 Niveau santé : {badge}")
        if next_level:
            st.info(
                f"✨ Objectif pour atteindre le niveau **{next_level}** : +{points_needed} pts en améliorant ton sommeil, ton sport ou ton alimentation !")
        else:
            st.success("🌟 Félicitations ! Tu as atteint le niveau maximum **Platine** 🎉")

        # Radar pour équilibre
        labels = ['IMC', 'Sport', 'Sommeil', 'Alimentation', 'Stress', 'Tabac/Alcool']
        values = [
            max(0, 25 - abs(22 - imc)) * 4,  # Sur 100
            min(activite_hebdo * 5, 100),
            min(sommeil * 10, 100),
            {"Peu équilibrée": 25, "Correcte": 50, "Bonne": 75, "Excellente": 100}[alimentation],
            max(0, 100 - stress * 10),
            100 - (15 if fumeur == "Régulier" else 5 if fumeur == "Occasionnel" else 0) - (
                10 if alcool == "Souvent" else 0)
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name='Profil Santé'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                angularaxis=dict(direction="clockwise")
            ),
            showlegend=False,
            title="Radar des Facteurs Santé"
        )

        st.subheader("📌 Équilibre global de tes facteurs santé")
        st.plotly_chart(fig_radar, use_container_width=True)

        # Conseils personnalisés
        st.subheader("💡 Conseils personnalisés")
        if score >= 80:
            st.success("✅ Tu es en super forme ! Continue tes bonnes habitudes.")
        elif score >= 60:
            st.info("🙂 Ton score est correct, mais tu peux optimiser ton sommeil, ton activité ou ton alimentation.")
        else:
            st.warning("⚠️ Score faible : améliore ton hygiène de vie et consulte un professionnel si besoin.")

        st.markdown("""
        **Recommandations :**
        - 🥗 **Alimentation** : Varie tes repas et privilégie les légumes/fruits.
        - 🏃‍♂️ **Activité physique** : Essaie d'ajouter 1 ou 2 séances de sport par semaine.
        - 😴 **Sommeil** : Tente de réguler ton sommeil (7-8h).
        - 🚭 **Tabac et alcool** : Réduis le tabac et l'alcool si possible.
        - 🧘‍♂️ **Stress** : Gère ton stress avec la relaxation ou la méditation.
        """)

        # Simulation d'historique
        np.random.seed(42)  # Pour reproductibilité
        nb_sessions = 20
        score_sante = np.random.randint(60, 90)  # valeur simulée sur 100
        score = score_sante
        historique_scores = np.clip(
            np.random.normal(loc=score, scale=5, size=nb_sessions),
            0, 100
        )
        sessions = list(range(1, nb_sessions + 1))
        score_min, score_max = historique_scores.min(), historique_scores.max()
        score_margin = (score_max - score_min) * 0.2

        # Graphique
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(
            x=sessions,
            y=historique_scores,
            mode='lines+markers',
            line=dict(color='mediumseagreen', width=3),
            marker=dict(size=7, color='darkgreen'),
            name='Score Santé',
            hovertemplate='Session %{x}<br>Score: %{y:.1f}<extra></extra>'
        ))
        fig_evo.update_layout(
            title="🧠 Suivi de ton Score Santé au fil des sessions",
            xaxis_title="Sessions",
            yaxis_title="Score Santé",
            yaxis=dict(
                range=[max(0, score_min - score_margin), min(100, score_max + score_margin)],
                tick0=0, dtick=10
            ),
            template="plotly_white",
            height=400,
            margin=dict(l=40, r=40, t=60, b=40)
        )

        # Affichage
        st.subheader("📈 Évolution de ton Score Santé")
        st.plotly_chart(fig_evo, use_container_width=True)

        # Partage sur réseaux sociaux
        st.markdown("### 🔗 Partage ton score")
        share_text = f"🎯 J'ai obtenu un Score Santé de {score:.1f}/100 sur AllHeart 💪 ! Et toi, tu fais combien ?"
        share_url = "https://fitpulse.app"  # Remplace par ton URL réelle
        tweet_text = urllib.parse.quote(f"{share_text} {share_url}")
        tweet_link = f"https://twitter.com/intent/tweet?text={tweet_text}"
        linkedin_link = f"https://www.linkedin.com/sharing/share-offsite/?url={urllib.parse.quote(share_url)}"
        facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(share_url)}"

        st.markdown("💬 Partage-le à tes amis :")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"[🐦 Twitter]({tweet_link})", unsafe_allow_html=True)
        with col2:
            st.markdown(f"[💼 LinkedIn]({linkedin_link})", unsafe_allow_html=True)
        with col3:
            st.markdown(f"[📘 Facebook]({facebook_link})", unsafe_allow_html=True)

        st.caption("Tu peux aussi copier ce texte :")
        st.code(share_text)


# --------- Gestion de la session ---------
if "client_connecte" not in st.session_state:
    st.session_state.client_connecte = None

#st.sidebar.image("/Users/fareesaamir/Desktop/Screenshot 2025-06-16 at 16.37.20.png",width = 100)

st.sidebar.title("ALL HEART")

st.sidebar.markdown(
    """
    Bienvenue dans la web application **ALL HEART**, ton espace de suivi bien-être et performance 💪  

    🧠 **Suis** l’évolution de ta santé physique et mentale  
    📊 **Visualise** tes progrès semaine après semaine  
    🎯 **Atteins** tes objectifs grâce à un accompagnement personnalisé  

    _Ta santé, ton rythme, ta victoire._
    """
)


# Menu de navigation
page = st.sidebar.selectbox("Choisis une option", ["Se connecter", "Créer un compte", "Se déconnecter"])
if page == ("Se déconnecter"):
    st.session_state.client_connecte = None
    st.rerun()

if page == "Se connecter":
    if st.session_state.client_connecte is None:
        st.subheader("Se connecter à votre compte")
        prenom = st.text_input("Prénom")
        nom = st.text_input("Nom")
        dob = st.date_input("Date de naissance", min_value=datetime.date(1900, 1, 1))

        if st.button("Se connecter"):
            st.balloons()
            clients = get_clients()
            client = find_client(clients, prenom, nom, dob)
            if client:
                st.success(f"Bienvenue {client['prenom']} {client['nom']} !")
                st.session_state.client_connecte = client
                st.rerun()

            else:
                st.error("Aucun compte trouvé avec ces informations.")
    else:
        # Affiche dashboard directement si déjà connecté
        show_dashboard(st.session_state.client_connecte)


elif page == "Créer un compte":
    st.subheader("Créer un nouveau compte client")

    nom = st.text_input("Nom *")
    prenom = st.text_input("Prénom *")
    dob = st.date_input("Date de naissance *", min_value=datetime.date(1900, 1, 1))
    email = st.text_input("Email *")
    telephone = st.text_input("Téléphone")
    objectif = st.text_area("Objectif sportif *")
    niveau = st.selectbox("Niveau sportif", ["Débutant", "Intermédiaire", "Avancé"])
    poids = st.number_input("Poids (kg)", min_value=20.0, max_value=300.0, step=0.1)
    taille = st.number_input("Taille (cm)", min_value=100, max_value=250)
    remarques = st.text_area("Remarques (santé, nutrition, blessures...)")

    if st.button("Créer le compte"):
        if nom and prenom and email and objectif:
            sheet_name = f"{prenom}_{nom}"
            data = {
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "objectif": objectif,
                "remarques": remarques,
                "dob": dob.isoformat(),
                "telephone": telephone,
                "niveau": niveau,
                "poids": poids,
                "taille": taille,
                "sheet_name": sheet_name,
            }

            try:
                response = requests.post(WEBHOOK_URL, data=data)
                if response.status_code == 200:
                    st.success(f"Compte créé et données enregistrées dans l'onglet « {sheet_name} » du Google Sheet.")
                else:
                    st.error(f"Erreur serveur : {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Erreur réseau : {e}")
        else:
            st.warning("Merci de remplir tous les champs obligatoires (*)")




#streamlit run main.py
#AKfycbwqyqRYnmL1pO7JB3Hd_XUudYMNrecuSxsO0Lpqqmbc3O-_1QuLRjRusa-qQJzQYf3CYg
#AKfycbyClKAQ-ZZg9i5ca0F3mJzeasbSsgbi5bFxdTTzf_LqZqZMP-nrUC1vQiiDxB-BBo27zw
#https://script.google.com/macros/s/AKfycbwqyqRYnmL1pO7JB3Hd_XUudYMNrecuSxsO0Lpqqmbc3O-_1QuLRjRusa-qQJzQYf3CYg/exec
#https://script.google.com/macros/s/AKfycbyClKAQ-ZZg9i5ca0F3mJzeasbSsgbi5bFxdTTzf_LqZqZMP-nrUC1vQiiDxB-BBo27zw/exec
#18yBQURMLqjvTWWkpmbEcalTab89PMixqis01hUp9EhU
