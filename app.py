import streamlit as st
import openai
import json

from chat2db.chat.azure import Azure
from chat2db.database.channel import Channel
from chat2db.prompts import load_prompt

st.title("Query GPT")

if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": load_prompt("router")}
    ]

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
    
    azure = Azure(st.secrets["OPENAI_API_KEY"], st.secrets["OPENAI_API_BASE"], st.secrets["ENGINE"])
    azure.azure_ask(st.session_state.messages)
    
    response = azure.azure_ask(st.session_state.messages)
    message_placeholder.markdown(full_response + "▌")

    for response in azure.azure_ask(st.session_state.messages):
        full_response += response
        message_placeholder.markdown(full_response + "▌")

    json_response = json.loads(full_response)
    db_name = ""
    channel = ""
    if json_response['response'].get('dbCheck') !='Yes':
        #TODO: 不查询数据库
        pass
    else:
        db_name = json_response['response'].get('dbName')
        keywods = json_response['response'].get('keywords')
        channel = Channel(db_name)
        

    message_placeholder.markdown(full_response)
    if db_name:
        table_names = ','.join(channel.target_tables).strip(',')
        table_schemas = channel.database_schema_string
        
        full_response += "\n\n"
        full_response += f"**:red[Database name]**: {db_name}\n\n"
        full_response += f"**:red[Table names]**: {table_names}\n\n"
        full_response += f"**:blue[Table Schemas]**: {table_schemas}\n\n"

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})