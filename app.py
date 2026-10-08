import streamlit as st
from google import genai
from google.genai import types
from groq import Groq

st.set_page_config(page_title="Correcteur CIM-ESUP", page_icon="icone.png")

client = genai.Client()
client_groq = Groq()

system_prompt = """Tu es un professeur d'anglais bienveillant mais exigeant.
Tu reçois un rapport quotidien écrit en anglais par un étudiant en mines.
Réponds toujours dans ce format :
1. version corrigée : le texte entièrement corrigé.
2. erreurs : chaque faute, avec la correction et une explication très simple en français.
3. conseil : une seule astuce pour progresser.
Si le texte n'a aucune faute, dis le clairement et félicite l'étudiant."""

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
                    response_grop = client_groq.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": rapport}
                        ],
                    )
                    text = response_grop.choices[0].message.content
                except Exception as e:
                    erreur = e
        if text:
            st.markdown(text)
        else:
            st.error("Une erreur est survenue lors de la correction. Veuillez réessayer plus tard.")
            st.caption(f"Détails de l'erreur : {erreur}")