import streamlit as st
import openai
import os

st.title("Query GPT")

openai.api_version = "2023-05-15"
openai.api_type = "azure"
# Set OpenAI API key and base from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
openai.api_base = st.secrets["OPENAI_API_BASE"]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's your question?"):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        ### print out the origin question
        st.markdown(f"Your question is: **:blue[{prompt}]**")

        message_placeholder = st.empty()
        full_response = ""
        
        

    for response in openai.ChatCompletion.create(
        engine ="gz_0613",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})