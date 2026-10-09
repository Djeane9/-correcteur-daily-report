import streamlit as st
from google import genai
from google.genai import types
from groq import Groq
import requests

st.set_page_config(page_title="Correcteur CIM-ESUP", page_icon="icone.png")

client = genai.Client()
client_groq = Groq()

@st.cache_data(ttl=86400)
def chercher_mot(mot):
    adresse = f"https://api.dictionaryapi.dev/api/v2/entries/en/{mot}"
    reponse = requests.get(adresse, timeout=20)
    if reponse.status_code == 200:
        return reponse.json()[0]
    return None 

@st.cache_data(ttl=86400)
def definition_ia (mot):
    consigne = f"Pour le mot anglais « {mot} », réponds uniquement avec deux lignes en français, sans introduction : « Traduction : ... » puis « Définition : ... » (une phrase très simple, pour un étudiant en mines débutant)."
    for modele in ["gemini-flash-lite-latest", "gemini-flash-latest"]:
        try:
            reponse = client.models.generate_content(model=modele, contents=consigne)
            return reponse.text
        except Exception:
            pass
    reponse_groq = client_groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": consigne}],
    )
    return reponse_groq.choices[0].message.content

system_prompt = """Tu es un professeur d'anglais bienveillant mais exigeant.
Tu reçois un rapport quotidien écrit en anglais par un étudiant en mines.
Réponds toujours dans ce format :
1. version corrigée : le texte entièrement corrigé.
2. erreurs : chaque faute, avec la correction et une explication très simple en français.
3. conseil : une seule astuce pour progresser.
4. mots : termine toujours ta réponse par une dernière ligne, au format exact « MOTS: mot1, mot2, mot3 », avec 3 mots anglais importants du rapport, sans aucun autre texte sur cette ligne.
Si le texte n'a aucune faute, dis-le clairement et félicite l'étudiant."""

st.image("logo.png", width=300)
st.title("Correcteur de Daily Report en anglais")
st.write("Club de l'Ingénierie Minière (CIM-ESUP), section anglaise")

rapport = st.text_area("Veuillez saisir votre Daily Report ici (en anglais) :", height=300)

modeles = ["gemini-flash-latest", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]

if st.button("Corriger", type="primary"):
    if rapport.strip() == "":
        st.warning("Veuillez écrire votre Daily Report avant de cliquer sur 'Corriger'.")
    else:
        with st.spinner("Correction en cours..."):
            text = None
            erreur = None
            for modele in modeles:
                try:
                    response = client.models.generate_content(
                        model=modele,
                        contents=rapport,
                        config=types.GenerateContentConfig(system_instruction=system_prompt)
                    )
                    text = response.text
                    break # Sortir de la boucle si la correction est réussie
                except Exception as e:
                    erreur = e
            if text is None:
                # Si aucune correction n'a été réussie, essayer avec Groq
                try:
                    response_groq = client_groq.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": rapport}
                        ],
                    )
                    text = response_groq.choices[0].message.content
                except Exception as e:
                    erreur = e
        if text:
            st.session_state["correction"] = text
        else:
            st.error("Une erreur est survenue lors de la correction. Veuillez réessayer plus tard.")
            st.caption(f"Détails de l'erreur : {erreur}")
if "correction" in st.session_state:
    correction = st.session_state["correction"]
    mots = []
    lignes_affichees = []

    for ligne in correction.splitlines():
        ligne_propre = ligne.replace("*", "").strip()
        if "MOTS:" in ligne_propre.upper():
            position = ligne_propre.upper().index("MOTS:")
            partie = ligne_propre[position + 5:]
            for m in partie.split(","):
                if m.strip() != "":
                    mots.append(m.strip())
        else:
            lignes_affichees.append(ligne)

    st.markdown("\n".join(lignes_affichees  ))

    if mots:
        st.subheader("Mots à retenir")
        for mot in mots [:3]:
            with st.expander(mot):
                try:
                    infos = chercher_mot(mot.lower())
                except Exception: 
                    infos = None
                if infos:
                    if infos.get("phonetic"):
                        st.write(infos["phonetics"])
                    for p in infos.get("phonetics", []):
                        if p.get("audio"):
                            st.audio(p["audio"])
                            break
                    sens = infos["meanings"][0]
                    st.markdown(f"**{sens['partOfSpeech']}** : {sens['definitions'][0]['definition']}")
                else:
                    try: 
                        st.write(definition_ia(mot.lower()))
                        st.caption("Définition générée par l'IA (dictionnaire non trouvé).")
                    except Exception:
                        st.write("Définition indisponible pour le moment.")
