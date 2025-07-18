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
from streamlit_option_menu import option_menu

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbws-rrMtZKiCSBTTg7pfVuDH93LcOM-RrDRayAerWsgMVVLPCOZGvP1fND6mcvZEI2oWg/exec"

st.set_page_config(
    page_title="Dashboard Client",
    page_icon="📊",
    layout="wide",      # Layout large
    initial_sidebar_state="expanded"
)

with st.sidebar:
    page = option_menu(
        "Menu",
        ["Se déconnecter", "Se connecter", "Créer un compte", "Page1"],
        icons=['box-arrow-right', 'box-arrow-in-right', 'person-plus'],  # 3 icônes pour 3 options
        menu_icon="cast",
        default_index=1,
        styles={
            "container": {
                "padding": "10px",
                "background-color": "#f8f9fa"
            },
            "icon": {
                "color": "#ff4b4b",
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": "#ffe6e6",
            },
            "nav-link-selected": {
                "background-color": "#ffcccc",
                "font-weight": "bold",
                "color": "black"
            },
        }    )

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
    # Définir les onglets
    tab1, tab3 = st.tabs([
        "👤 Infos personnelles",
        "🗒️ Suivi personnalisé "    ])

    def example():
        col1, col2, col3 = st.columns(3)

        col1.metric(label="Gain", value=5000, delta=1000)
        col2.metric(label="Loss", value=5000, delta=-1000)
        col3.metric(label="No Change", value=5000, delta=0)

        style_metric_cards()

    with tab1:
        # 📂 Informations personnelles
        with st.expander("ℹ️ Détails personnels", expanded=True):
            st.header(client["prenom"])

            infos = {
                "📧 Email": client.get("email", "Non spécifié"),
                "📞 Téléphone": client.get("telephone", "Non spécifié"),
                "🏋️ Niveau sportif": client.get("niveau", "Non spécifié"),
                "🎯 Objectif": client.get("objectif", "Non spécifié"),
                "📝 Remarques": client.get("remarques", "Aucune"),
                "⚖️ Poids (kg)": client.get("poids", "Non spécifié"),
                "📏 Taille (cm)": client.get("taille", "Non spécifié"),
                "🎂 Date de naissance": client.get("dob", "Non spécifiée")
            }

            col0, col1, col2, col3 = st.columns([1, 2, 2, 1])

            with col0:
                st.image(
                    "Screenshot 2025-06-16 at 16.37.20.png",
                    width=180,
                    caption=client.get("prenom", "Profil"),
                )
                st.markdown(
                    """
                    <style>
                    img {
                        border-radius: 15px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

            for idx, (key, val) in enumerate(infos.items()):
                with col1 if idx % 2 == 0 else col2:
                    st.markdown(f"**{key}:** {val}")

            with col3:
                st.metric(label="Objectif Réalisé", value="85%", delta="5% depuis le dernier mois")

            # Ajout de styles CSS supplémentaires pour améliorer l'apparence
            st.markdown(
                """
                <style>
                .stMetric {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        st.subheader("🎯 Progression vers l’objectif")

        progress = (float(85) - 67) / (float(85))
        st.progress(min(max(progress, 0), 1))
        # ---------------------------

        st.metric(label="Composition corporelle ", value="Pas encore évalué", delta=1000,
                  border=True)

        @st.dialog("Formulaire de compo corporelle")

        def health_form():
            st.write("## 🩺 Questionnaire Santé Complet")

            # --- Infos de base ---
            poids = st.number_input("⚖️ Quel est votre poids (en kg) ?", min_value=0.0, step=0.1, key="poids_input")
            taille = st.number_input("📏 Quelle est votre taille (en cm) ?", min_value=0.0, step=0.1,
                                     key="taille_input")
            age = st.number_input("🎂 Quel est votre âge ?", min_value=0, max_value=120, step=1, key="age_input")

            # --- Habitudes de vie ---
            sommeil = st.slider("😴 Combien d'heures dormez-vous par nuit ?", 0, 12, value=7, key="sommeil_input")
            hydratation = st.slider("💧 Combien de verres d’eau buvez-vous par jour ?", 0, 15, value=6,
                                    key="hydratation_input")
            fumeur = st.radio("🚬 Êtes-vous fumeur ?", ["Oui", "Non"], key="fumeur_input")
            alcool = st.radio("🍷 Consommez-vous de l’alcool régulièrement ?", ["Oui", "Non"], key="alcool_input")
            activite = st.selectbox("🏃‍♂️ Fréquence d'activité physique par semaine",
                                    ["Aucune", "1-2 fois", "3-4 fois", "5 fois ou plus"], key="activite_input")
            alimentation = st.selectbox("🥗 Qualité de votre alimentation",
                                        ["Mauvaise", "Moyenne", "Bonne", "Excellente"], key="alimentation_input")
            stress = st.slider("⚡ Niveau de stress perçu (0 = aucun, 10 = extrême)", 0, 10, 5, key="stress_input")

            # --- Antécédents santé ---
            douleurs = st.radio("🤕 Ressentez-vous des douleurs chroniques ?", ["Oui", "Non"], key="douleurs_input")
            maladies = st.multiselect("🏥 Avez-vous des antécédents médicaux ?",
                                      ["Hypertension", "Diabète", "Cardiaque", "Respiratoire", "Autres", "Aucun"],
                                      key="maladies_input")

            # --- Validation ---
            if st.button("✅ Calculer mon score santé"):
                if poids == 0 or taille == 0 or age == 0:
                    st.warning("⚠️ Merci de saisir un poids, une taille et un âge valides.")
                    return

                # --- Calcul IMC ---
                imc = poids / ((taille / 100) ** 2)

                # --- Calcul du pourcentage de graisse corporelle estimé ---
                # Formule de Deurenberg pour les adultes
                body_fat_percentage = 1.2 * imc + 0.23 * age - 10.8 * 1 - 5.4

                # --- Base score ---
                score = 100

                # Poids / IMC
                if imc < 18.5 or imc > 24.9:
                    score -= 15

                # Sommeil
                if sommeil < 7 or sommeil > 9:
                    score -= 10

                # Hydratation
                if hydratation < 5:
                    score -= 5

                # Fumeur / Alcool
                if fumeur == "Oui":
                    score -= 20

                if alcool == "Oui":
                    score -= 5

                # Activité physique
                activite_points = {"Aucune": 0, "1-2 fois": 10, "3-4 fois": 20, "5 fois ou plus": 30}
                score += activite_points.get(activite, 0)

                # Alimentation
                alimentation_points = {"Mauvaise": 0, "Moyenne": 10, "Bonne": 20, "Excellente": 30}
                score += alimentation_points.get(alimentation, 0)

                # Stress
                score -= stress * 2

                # Douleurs / Maladies
                if douleurs == "Oui":
                    score -= 10

                if "Hypertension" in maladies or "Diabète" in maladies or "Cardiaque" in maladies:
                    score -= 10

                # Score final borné
                score = max(0, min(score, 100))

                # --- Sauvegarde ---
                st.session_state.health_data = {
                    "poids": poids,
                    "taille": taille,
                    "age": age,
                    "imc": round(imc, 1),
                    "body_fat_percentage": round(body_fat_percentage, 1),
                    "sommeil": sommeil,
                    "hydratation": hydratation,
                    "fumeur": fumeur,
                    "alcool": alcool,
                    "activite": activite,
                    "alimentation": alimentation,
                    "stress": stress,
                    "douleurs": douleurs,
                    "maladies": maladies,
                    "score": score,
                }

                st.toast("✅ Questionnaire soumis avec succès !")
                show_result()  # Affiche le résultat immédiatement

        def show_result():
            data = st.session_state.health_data
            st.write("📊 Résultat de votre évaluation santé")

            score = data['score']
            imc = data['imc']
            body_fat_percentage = data['body_fat_percentage']

            # --- Niveau de santé ---
            if score >= 80:
                st.success(f"🟢 Excellent ! Votre score santé est **{score}/100** ✅")
            elif score >= 50:
                st.warning(f"🟠 Moyen : Votre score santé est **{score}/100**. Il y a des points à améliorer.")
            else:
                st.error(
                    f"🔴 Faible : Votre score santé est **{score}/100**. Une amélioration est fortement conseillée.")

            # --- IMC ---
            st.info(f"📏 **IMC : {imc}** (idéal entre 18.5 et 24.9)")
            st.info(f"📉 **Pourcentage de graisse corporelle estimé : {body_fat_percentage}%**")

            # --- Conseils personnalisés ---
            st.write("### 📝 Conseils personnalisés")

            if imc < 18.5:
                st.write(
                    "🔹 **Vous êtes en sous-poids.** Consultez un professionnel pour adapter votre alimentation.")
            elif imc > 24.9:
                st.write(
                    "🔹 **Votre IMC est au-dessus de la normale.** Une activité physique et une alimentation adaptée peuvent aider.")

            if body_fat_percentage > 25:  # Seuil indicatif pour les hommes
                st.write(
                    "🔹 **Votre pourcentage de graisse corporelle est élevé.** Envisagez de consulter un professionnel pour un plan personnalisé.")

            if data['sommeil'] < 7:
                st.write("🔹 **Vous dormez trop peu.** Essayez d’avoir entre 7 et 9h de sommeil.")

            if data['hydratation'] < 5:
                st.write("🔹 **Buvez plus d’eau.** Visez au moins 1.5 à 2L par jour.")

            if data['fumeur'] == "Oui":
                st.write("🔹 **Arrêter de fumer améliorerait significativement votre santé.**")

            if data['stress'] > 7:
                st.write("🔹 **Votre stress est élevé.** Envisagez des techniques de relaxation ou de méditation.")

            if data['activite'] == "Aucune":
                st.write(
                    "🔹 **Ajoutez une activité physique régulière.** Même 30 minutes de marche par jour aident beaucoup.")

            # --- Boutons finaux ---
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Refaire le questionnaire"):
                    st.session_state.pop("health_data", None)
                    st.rerun()

            with col2:
                st.link_button("📅 Prendre RDV avec un coach", "https://calendly.com/")
            with col3:
                if st.button(" Quitter le questionnaire"):
                    st.session_state.show_form = False  # ✅ On ferme le formulaire

        if "health_data" not in st.session_state:
            if st.button("Remplir mon questionnaire santé"):
                st.session_state.show_form = True

            if st.session_state.get("show_form", False):
                health_form()
        else:
            with st.expander("📊 Voir mon score santé", expanded=True):
                show_result()

        st.divider()

        st.metric(
            label="💪 Score de performance physique",
            value="Pas encore évalué",
            delta="⏳ En attente",
            border=True
        )
        if st.button("📝 Remplir le questionnaire santé", type="primary"):
            st.session_state.current_page = "Page1"  # ✅ on change la page
            page = "Page1"
            st.rerun()

        st.divider()

        st.metric(
            label="📊 État général & suivi santé",
            value="Pas encore disponible",
            delta="⏳ En attente",
            border=True
        )
        if st.button("🔄 Rafraîchir les données", type="primary"):
            st.session_state.show_form = False
            st.rerun()

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


# --------- Gestion de la session ---------
if "client_connecte" not in st.session_state:
    st.session_state.client_connecte = None

#st.sidebar.image("/Users/fareesaamir/Desktop/Screenshot 2025-06-16 at 16.37.20.png",width = 100)




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

if page == "Page1":
    if st.session_state.client_connecte is None:
        st.subheader("Connectez vous")
    else:
        st.title("🩺 Bilan Santé Complet")

        with st.form("form_sante_complet"):
            st.subheader("1️⃣ Informations générales")
            age = st.slider("Âge", 10, 100, 30)
            taille = st.number_input("Taille (en cm)", min_value=100, max_value=250, value=170)
            poids = st.number_input("Poids (en kg)", min_value=30, max_value=200, value=70)
            sexe = st.radio("Sexe", ["Homme", "Femme", "Autre"])

            st.subheader("2️⃣ Habitudes de vie")
            sport = st.selectbox("Fréquence d’activité physique", ["Jamais", "1-2 fois/semaine", "3-4 fois/semaine", "Quotidiennement"])
            sommeil = st.slider("Heures de sommeil en moyenne", 3, 12, 7)
            alimentation = st.selectbox("Comment évaluez-vous votre alimentation ?", ["Très mauvaise", "Moyenne", "Bonne", "Excellente"])
            hydratation = st.slider("Verres d’eau par jour", 0, 15, 6)
            alcool = st.selectbox("Consommation d’alcool", ["Jamais", "Occasionnelle", "Régulière"])
            tabac = st.selectbox("Consommation de tabac", ["Non-fumeur", "Fumeur occasionnel", "Fumeur régulier"])

            st.subheader("3️⃣ Santé mentale & énergie")
            stress = st.slider("Niveau de stress (0 = aucun, 10 = très élevé)", 0, 10, 5)
            humeur = st.selectbox("Votre humeur globale", ["Mauvaise", "Moyenne", "Bonne", "Excellente"])
            energie = st.slider("Votre niveau d’énergie quotidien (0 = épuisé, 10 = plein d’énergie)", 0, 10, 6)

            st.subheader("4️⃣ Antécédents médicaux")
            maladies = st.multiselect("Avez-vous des maladies chroniques ?", ["Hypertension", "Diabète", "Asthme", "Maladies cardiaques", "Troubles digestifs", "Aucune"])
            medicaments = st.radio("Prenez-vous des médicaments régulièrement ?", ["Oui", "Non"])

            st.subheader("5️⃣ Symptômes actuels")
            symptomes = st.multiselect("Avez-vous ressenti récemment ces symptômes ?", ["Fatigue", "Douleurs musculaires", "Maux de tête", "Problèmes digestifs", "Difficultés respiratoires", "Aucun"])

            st.subheader("6️⃣ Douleurs ou inconfort")
            douleurs = st.selectbox("Avez-vous des douleurs physiques ?", ["Aucune", "Occasionnelles", "Fréquentes", "Chroniques"])
            mobilite = st.slider("Évaluez votre mobilité générale (0 = très limitée, 10 = parfaite)", 0, 10, 8)

            submitted = st.form_submit_button("✅ Calculer mon score santé")

        # -------- CALCUL DU SCORE --------
        def calculer_score():
            score = 100

            # Calcul de l'IMC
            imc = poids / ((taille / 100) ** 2)
            if imc < 18.5 or imc > 30:
                score -= 10

            # Calcul du pourcentage de graisse corporelle estimé
            if sexe == "Homme":
                body_fat_percentage = 1.20 * imc + 0.23 * age - 16.2
            else:
                body_fat_percentage = 1.20 * imc + 0.23 * age - 5.4

            # Sport
            if sport == "Jamais":
                score -= 20
            elif sport == "1-2 fois/semaine":
                score -= 10

            # Sommeil
            if sommeil < 6 or sommeil > 9:
                score -= 10

            # Hydratation
            if hydratation < 5:
                score -= 5

            # Alimentation
            if alimentation == "Très mauvaise":
                score -= 20
            elif alimentation == "Moyenne":
                score -= 10

            # Alcool & Tabac
            if alcool == "Régulière":
                score -= 10
            if tabac != "Non-fumeur":
                score -= 15

            # Stress & énergie
            if stress > 7:
                score -= 10
            if energie < 5:
                score -= 10

            # Maladies chroniques
            if "Aucune" not in maladies and len(maladies) > 0:
                score -= 15

            # Symptômes
            if "Aucun" not in symptomes and len(symptomes) > 0:
                score -= 10

            # Médicaments réguliers
            if medicaments == "Oui":
                score -= 5

            # Douleurs & mobilité
            if douleurs in ["Fréquentes", "Chroniques"]:
                score -= 10
            if mobilite < 5:
                score -= 10

            return max(0, min(score, 100)), imc, body_fat_percentage

        # -------- AFFICHAGE DES RESULTATS --------
        if submitted:
            score, imc, body_fat_percentage = calculer_score()
            st.subheader("📊 Résultat de votre bilan")
            st.metric("Votre score santé", f"{score}/100")

            # Interprétation
            if score >= 80:
                st.success("✅ Excellent état de santé global ! Continuez ainsi 💪")
            elif score >= 60:
                st.warning("⚠️ Santé correcte mais quelques points à améliorer.")
            else:
                st.error("❌ Santé fragile, il est conseillé de consulter un professionnel.")

            # IMC info
            st.write(f"Votre IMC est **{imc:.1f}**")
            if imc < 18.5:
                st.write("⚠️ Vous êtes en **insuffisance pondérale**.")
            elif imc > 30:
                st.write("⚠️ Vous êtes en **obésité**.")
            elif imc > 25:
                st.write("⚠️ Vous êtes en **surpoids**.")
            else:
                st.write("✅ Votre IMC est **normal**.")

            # Pourcentage de graisse corporelle
            st.write(f"Votre pourcentage de graisse corporelle estimé est **{body_fat_percentage:.1f}%**")
            if body_fat_percentage > 25:  # Seuil indicatif pour les hommes
                st.write("⚠️ Votre pourcentage de graisse corporelle est **élevé**.")

            # Conseils supplémentaires
            st.subheader("📝 Conseils personnalisés")
            if imc < 18.5 or imc > 25:
                st.write("🔹 Consultez un professionnel pour adapter votre alimentation et votre activité physique.")
            if body_fat_percentage > 25:
                st.write("🔹 Envisagez de consulter un professionnel pour un plan personnalisé.")
            if sport == "Jamais":
                st.write("🔹 Ajoutez une activité physique régulière. Même 30 minutes de marche par jour aident beaucoup.")
            if stress > 7:
                st.write("🔹 Votre stress est élevé. Envisagez des techniques de relaxation ou de méditation.")
            if tabac != "Non-fumeur":
                st.write("🔹 Arrêter de fumer améliorerait significativement votre santé.")

            # Boutons après le résultat
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refaire le questionnaire"):
                    st.experimental_rerun()
            with col2:
                if st.button("📅 Prendre rendez-vous avec un coach"):
                    st.markdown("[👉 Cliquez ici pour réserver votre séance](https://calendly.com/)")


#streamlit run main.py
#AKfycbwqyqRYnmL1pO7JB3Hd_XUudYMNrecuSxsO0Lpqqmbc3O-_1QuLRjRusa-qQJzQYf3CYg
#AKfycbyClKAQ-ZZg9i5ca0F3mJzeasbSsgbi5bFxdTTzf_LqZqZMP-nrUC1vQiiDxB-BBo27zw
#https://script.google.com/macros/s/AKfycbwqyqRYnmL1pO7JB3Hd_XUudYMNrecuSxsO0Lpqqmbc3O-_1QuLRjRusa-qQJzQYf3CYg/exec
#https://script.google.com/macros/s/AKfycbyClKAQ-ZZg9i5ca0F3mJzeasbSsgbi5bFxdTTzf_LqZqZMP-nrUC1vQiiDxB-BBo27zw/exec
#18yBQURMLqjvTWWkpmbEcalTab89PMixqis01hUp9EhU
