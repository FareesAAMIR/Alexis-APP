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
import base64
import altair as alt
import urllib.parse
from streamlit_extras.sandbox import sandbox
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit import expander
from streamlit_option_menu import option_menu

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzgzxotlsMo48YTeGYn8Y5WARCsqyOys2Dlj-e3VYvJVnC8NWXKeMc77wCSZW2vtyuuJA/exec"

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

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
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
                    client.get("photo_profil"),
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
        sheet_name = f"{client['prenom']}_{client['nom']}"

        response = requests.get(f"{WEBHOOK_URL}?sheet_name={sheet_name}")

        data = response.json()
        scores = data.get("scores", [])

        # 🔹 Récupération du dernier score
        if scores:
            last_score = scores[-1]["score"]  # dernier enregistré
        else:
            last_score = "Pas encore évalué"

        st.metric(label="IMC", value=last_score, delta="Dernier score calculé",
                  border=True)

        @st.dialog("Formulaire de compo corporelle")

        def health_form():
            st.write("## 🩺 Questionnaire Santé Complet")
            poids_defaut = client.get("poids")

            try:
                poids_defaut = float(poids_defaut)
            except (TypeError, ValueError):
                poids_defaut = 0.0
                # --- Infos de base ---
            poids = st.number_input("⚖️ Quel est votre poids (en kg) ?", min_value=0.0, value=float(client.get("poids") or 0.0),step=0.1, key="poids_input")
            taille = float(client.get("taille"))

            # --- Validation ---
            if st.button("✅ Calculer mon score santé"):
                if poids == 0:
                    st.warning("⚠️ Merci de saisir un poids, une taille et un âge valides.")
                    return

                # --- Calcul IMC ---
                imc = poids / ((taille / 100) ** 2)

                score = 100

                score = max(0, min(score, 100))
                scor = score
                # --- Sauvegarde ---
                st.session_state.health_data = {
                    "poids": poids,
                    "taille": taille,
                    "imc": round(imc, 1),
                    "score": score,
                }

                st.toast("✅ Questionnaire soumis avec succès !")
                sheet_name = f"{client['prenom']}_{client['nom']}"
                data1 = {
                    "action": "update_scor",  # <-- tu peux ajouter un champ pour indiquer l'action côté Apps Script
                    "sheet_name": sheet_name,
                    "scor": scor
                }
                try:
                    response = requests.post(WEBHOOK_URL, data=data1, timeout=10)
                    if response.status_code == 200:
                        st.success("✅ Ton score santé a bien été ajouté à ton compte !")
                    else:
                        st.error(f"❌ Erreur serveur : {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Erreur réseau : {e}")

                show_result()  # Affiche le résultat immédiatement

        def show_result():
            data = st.session_state.health_data
            st.write("📊 Résultat de votre évaluation santé")

            score = data['score']
            imc = data['imc']

            # --- Affichage IMC ---
            st.subheader(f"📏 Votre IMC : **{imc:.1f}**")

            # Échelle IMC
            imc_scale = [
                ("< 16", "Dénutrition", "🔴"),
                ("16 - 18.4", "Sous-poids", "🟠"),
                ("18.5 - 24.9", "Normal", "🟢"),
                ("25 - 29.9", "Surpoids", "🟠"),
                ("≥ 30", "Obésité", "🔴")
            ]

            # --- Trouver la catégorie ---
            if imc < 16:
                category = "Dénutrition"
                color = "red"
            elif imc < 18.5:
                category = "Sous-poids"
                color = "orange"
            elif imc <= 24.9:
                category = "Poids normal"
                color = "green"
            elif imc <= 29.9:
                category = "Surpoids"
                color = "orange"
            else:
                category = "Obésité"
                color = "red"

            st.markdown(f"📌 **Catégorie : <span style='color:{color}'>{category}</span>**", unsafe_allow_html=True)


            # --- Conseils personnalisés ---
            st.write("### 📝 Conseils personnalisés")

            if imc < 18.5:
                st.warning("🔹 **Vous êtes en sous-poids.** Consultez un professionnel pour adapter votre alimentation.")
            elif imc > 24.9:
                st.warning(
                    "🔹 **Votre IMC est au-dessus de la normale.** Une activité physique et une alimentation adaptée peuvent aider.")
            else:
                st.success("✅ Votre IMC est dans la zone optimale. Continuez à adopter un mode de vie sain !")

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

        with st.expander("Voir mon historique score santé", expanded=False):
            sheet_name = f"{client['prenom']}_{client['nom']}"
            try:
                # Appel GET pour récupérer les scores
                response = requests.get(f"{WEBHOOK_URL}?sheet_name={sheet_name}")
                if response.status_code == 200:
                    data = response.json()

                    if "error" in data:
                        st.warning("Aucun historique trouvé pour ce compte.")
                    else:
                        scores = data.get("scores", [])

                        if not scores:
                            st.info("Pas encore de score enregistré.")
                        else:
                            df = pd.DataFrame(scores)
                            st.subheader("📊 Historique de tes scores santé")
                            st.dataframe(df)

                            # Affichage graphique
                            df["date"] = pd.to_datetime(df["date"], errors="coerce")
                            df = df.dropna(subset=["date"])
                            if not df.empty:
                                st.line_chart(df.set_index("date")["score"])
                else:
                    st.error(f"Erreur serveur : {response.status_code}")
            except Exception as e:
                st.error(f"Erreur réseau : {e}")

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

    # === Objectifs et niveau ===
    st.write("### 🏋️ Objectifs sportifs")
    objectif = st.selectbox(
        "Objectif sportif *",
        [
            "Perte de poids",
            "Prise de masse musculaire",
            "Amélioration de l’endurance",
            "Préparation à une compétition",
            "Remise en forme générale",
            "Rééducation / récupération",
            "Autre"
        ]
    )
    niveau = st.selectbox("Niveau sportif", ["Débutant", "Intermédiaire", "Avancé"])

    # === Données physiques ===
    st.write("### ⚖️ Données physiques")
    poids = st.number_input("Poids (kg)", min_value=20.0, max_value=300.0, step=0.1)
    taille = st.number_input("Taille (cm)", min_value=100, max_value=250)

    # === Remarques libres ===
    st.write("### 📝 Informations complémentaires")
    remarques = st.text_area("Remarques (santé, nutrition, blessures...)")

    enable = st.checkbox("Enable camera")
    picture = st.camera_input("Take a picture", disabled=not enable)

    avatars = {
        "Avatar 1": "https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShortCurly&accessoriesType=Blank&hairColor=Brown&facialHairType=Blank&clotheType=Hoodie&clotheColor=PastelBlue&eyeType=Happy&eyebrowType=Default&mouthType=Smile&skinColor=Light",
        "Avatar 2": "https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Round&hairColor=Blonde&facialHairType=Blank&clotheType=BlazerShirt&clotheColor=PastelGreen&eyeType=Wink&eyebrowType=RaisedExcited&mouthType=Default&skinColor=Light",
        "Avatar 3": "https://avataaars.io/?avatarStyle=Circle&topType=ShortHairDreads01&accessoriesType=Blank&hairColor=Black&facialHairType=MoustacheMagnum&facialHairColor=Black&clotheType=ShirtCrewNeck&clotheColor=PastelOrange&eyeType=Squint&eyebrowType=UpDown&mouthType=Smile&skinColor=Brown",
        "Avatar 4": "https://avataaars.io/?avatarStyle=Circle&topType=Hijab&accessoriesType=Kurt&hairColor=BrownDark&facialHairType=Blank&clotheType=ShirtVNeck&clotheColor=Blue03&eyeType=Happy&eyebrowType=DefaultNatural&mouthType=Smile&skinColor=Light",
        "Avatar 5": "https://avataaars.io/?avatarStyle=Circle&topType=ShortHairFrizzle&accessoriesType=Prescription02&hairColor=Red&facialHairType=Blank&clotheType=GraphicShirt&clotheColor=Gray02&eyeType=EyeRoll&eyebrowType=AngryNatural&mouthType=Twinkle&skinColor=Tanned",
        "Avatar 6": "https://avataaars.io/?avatarStyle=Circle&topType=LongHairCurly&accessoriesType=Blank&hairColor=PastelPink&facialHairType=Blank&clotheType=BlazerSweater&clotheColor=Gray01&eyeType=Default&eyebrowType=FlatNatural&mouthType=Default&skinColor=Pale",
        "Avatar 7": "https://avataaars.io/?avatarStyle=Circle&topType=Eyepatch&accessoriesType=Wayfarers&hairColor=BrownDark&facialHairType=BeardMedium&facialHairColor=BrownDark&clotheType=Hoodie&clotheColor=Heather&eyeType=Close&eyebrowType=SadConcerned&mouthType=Serious&skinColor=DarkBrown",
        "Avatar 8": "https://avataaars.io/?avatarStyle=Circle&topType=LongHairBob&accessoriesType=Sunglasses&hairColor=Auburn&facialHairType=Blank&clotheType=ShirtScoopNeck&clotheColor=PastelYellow&eyeType=Hearts&eyebrowType=Default&mouthType=Smile&skinColor=Light"
    }

    st.write("### Choisissez votre image de profil")

    # Affiche toutes les images avec leur nom, l'utilisateur sélectionne par exemple via un selectbox
    choix_avatar = st.selectbox("Sélectionnez un avatar", options=list(avatars.keys()))

    # Affiche l'image sélectionnée
    st.image(avatars[choix_avatar], width=150)

    # Quand tu récupères les données à envoyer, tu peux récupérer le lien ou charger l'image en base64
    photo_profil_url = avatars[choix_avatar]

    if picture:
        # Convertir la photo en base64 (chaîne de texte)
        photo_base64 = base64.b64encode(picture.getvalue()).decode("utf-8")
    else:
        photo_base64 = None

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
                "photo_profil": photo_profil_url,
            }

            try:
                response = requests.post(WEBHOOK_URL, data=data)
                if response.status_code == 200:
                    st.success(f"Ton compte a été crée {prenom}, connecte toi pour accéder à ton compte ! ")
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
        st.title("Bilan Santé Complet")



#streamlit run main.py


