import streamlit as st

st.title("Query GPT")

if prompt := st.chat_input("What's your question?"):
    st.markdown(f"Your question is：**:blue[{prompt}]**")
    