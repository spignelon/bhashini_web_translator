import streamlit as st
import os
import webbrowser
lang={  "Hindi":1,
        "Gom":2,
        "Kannada":3,
        "Dogri":4,
        "Bodo":5,
        "Urdu":6,
        "Tamil":7,
        "Kashmiri":8,
        "Assamese":9,
         "Bengali":10,
         "Marathi":11,
         "Sindhi":12,
         "Maithili":13,
         "Punjabi":14,
         "Malayalam":15,
         "Manipuri":16,
         "Telugu":17,
         "Sanskrit":18,
         "Nepali":19,
         "Santali":20,
         "Gujarati":21,
         "Odia":22,
         "English":23}
st.header("AI Techies: Indic Language Support")


input0 = st.text_input("Enter the website link",key="input0")
i1 = st.selectbox('Select language 1', list(lang.keys()),key="i1")
i2 = st.selectbox('Select language 2', list(lang.keys()),key="i2")
l1=lang[i1]
l2=lang[i2]
if st.button("Translate"):
    if(i1==i2):
        st.write("Target and Source Language can't be same")
    else:
        link = "https://815d-2409-40d0-17-ac06-3c4b-50cc-6535-1a7c.ngrok-free.app/translate_webpage/" + str(l1) + "/" + str(l2) + "/" + input0
        webbrowser.open(link)
        st.write(f"Translation Link: [link]({link})")

