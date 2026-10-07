import streamlit as st
from google import genai
from google.genai import types

client = genai.Client()

system_prompt = """Tu es un professeur d'anglais bienveillant mais exigeant.
Tu reçois un rapport quotidien écrit en anglais par un étudiant en mines.
Réponds toujours dans ce format :
1. version corrigée : le texte entièrement corrigé.
2. erreurs : chaque faute, avec la correction et une explication très simple en français.
3. conseil : une seule astuce pour progresser.
Si le texte n'a aucune faute, dis le clairement et félicite l'étudiant."""

st.title("Correcteur de Daily Report en anglais")
st.write("Club des Miniers, section anglaise")

rapport = st.text_area("Veuillez saisir votre Daily Report ici (en anglais) :", height=300)

if st.button("Corriger"):
    if rapport.strip() == "":
        st.warning("Veuillez écrire votre Daily Report avant de cliquer sur 'Corriger'.")
    else:
        with st.spinner("Correction en cours..."):
            try:
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=rapport,
                    config=types.GenerateContentConfig(system_instruction=system_prompt)
            )
                st.markdown(response.text)
            except Exception as e:
                st.error("Une erreur est survenue lors de la correction. Veuillez réessayer plus tard.")
                st.caption(f"Détails de l'erreur : {e}")
