import streamlit as st

st.set_page_config(page_title="Docker + Poetry + Streamlit", page_icon="🚀")
st.title("Mangetamain Docker + Poetry + Streamlit 🚀")
name = st.text_input("Test input", "Type your name test")
if name:
    st.success(f"Welcome, {name}!")