import streamlit as st

st.set_page_config(page_title="MediaGuard")
st.title("MediaGuard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Check", "Request", "Org Portal", "Admin"
])