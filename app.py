# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="FlashCourse - Apprenez en 5 jours", page_icon="⚡", layout="wide")

# Custom CSS pour un look moderne
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    .stSidebar { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .quiz-container { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE L'API GEMINI ---
# Remplacez la partie "INITIALISATION DE L'API GEMINI" par ceci :
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("Configuration manquante : La clé API n'est pas configurée dans les secrets.")

# --- FONCTIONS UTILES ---
def generate_course(topic):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Crée un cours complet et pédagogique sur le sujet suivant : "{topic}".
    Le cours doit être divisé en 5 jours distincts.
    Pour chaque jour, fournis :
    1. Une leçon détaillée (environ 300 mots).
    2. Un quiz de 3 questions à choix multiples (QCM).
    
    Format de réponse attendu (JSON uniquement) :
    {{
      "Jour 1": {{
        "titre": "Titre du jour 1",
        "lecon": "Contenu de la leçon...",
        "quiz": [
          {{"question": "Question 1", "options": ["A", "B", "C", "D"], "reponse": "A"}},
          ...
        ]
      }},
      ... jusqu'au Jour 5
    }}
    Réponds uniquement avec le JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        # Nettoyage de la réponse pour extraire le JSON au cas où Gemini ajoute du texte Markdown
        json_str = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")
        return None

# --- GESTION DE L'ÉTAT (SESSION STATE) ---
if 'course_data' not in st.session_state:
    st.session_state.course_data = None
if 'current_day' not in st.session_state:
    st.session_state.current_day = "Jour 1"

# --- INTERFACE UTILISATEUR ---

st.title("⚡ FlashCourse")
st.subheader("Maîtrisez n'importe quel sujet en seulement 5 jours.")

# Champ de saisie principal
topic = st.text_input("Que souhaitez-vous apprendre aujourd'hui ?", placeholder="ex: La physique quantique, le jardinage japonais, Python...")

if st.button("Générer le cours"):
    if not api_key:
        st.error("Clé API manquante !")
    elif topic:
        with st.spinner("Génération de votre programme personnalisé par Gemini..."):
            course = generate_course(topic)
            if course:
                st.session_state.course_data = course
                st.success("Cours généré avec succès !")
    else:
        st.warning("Veuillez entrer un sujet.")

# --- AFFICHAGE DU COURS ---
if st.session_state.course_data:
    # Sidebar pour la navigation
    days = list(st.session_state.course_data.keys())
    st.sidebar.title("📅 Programme")
    selected_day = st.sidebar.radio("Aller au :", days)
    st.session_state.current_day = selected_day

    # Contenu principal
    data = st.session_state.course_data[st.session_state.current_day]
    
    st.divider()
    st.header(f"🌟 {st.session_state.current_day} : {data['titre']}")
    
    # Onglets pour séparer Leçon et Quiz
    tab1, tab2 = st.tabs(["📚 Leçon", "✍️ Quiz"])
    
    with tab1:
        st.markdown(data['lecon'])
    
    with tab2:
        st.subheader("Testez vos connaissances")
        score = 0
        for i, q in enumerate(data['quiz']):
            st.write(f"**Question {i+1}:** {q['question']}")
            # Utilisation d'une clé unique pour chaque widget afin d'éviter les conflits de session
            answer = st.radio(f"Sélectionnez une réponse pour Q{i+1}:", q['options'], key=f"q_{st.session_state.current_day}_{i}")
            
            if st.button(f"Vérifier Q{i+1}", key=f"btn_{st.session_state.current_day}_{i}"):
                if answer == q['reponse']:
                    st.success("Correct !")
                else:
                    st.error(f"Faux. La bonne réponse était : {q['reponse']}")

else:
    st.info("Entrez un sujet ci-dessus pour commencer votre aventure d'apprentissage.")
