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
        message_placeholder_chart = st.empty()
        analysis_response = ""

    azure = Azure(st.secrets["OPENAI_API_KEY"], st.secrets["OPENAI_API_BASE"], st.secrets["ENGINE"])
    # azure.azure_ask(st.session_state.messages)

    # response = azure.azure_ask(st.session_state.messages)
    # message_placeholder.markdown(full_response + "▌")

    for response in azure.azure_ask(st.session_state.messages):
        analysis_response += response
        # message_placeholder.markdown(full_response + "▌")
    # print(full_response)
    json_response = json.loads(analysis_response)

    if json_response['response'].get('dbCheck') != 'Yes':
        # TODO: 不查询数据库
        pass
    else:
        db_name = json_response['response'].get('dbName')
        keywods = [i for i in json_response['response'].get('keywords')]
        channel = Channel(db_name)

        step1 = '### **Step 1: Analysis prompt generates [Analysis Context]**\n'
        output = step1 + analysis_response

        table_names = ','.join(channel.target_tables).strip(',')
        table_schemas = channel.database_schema_string
        analysis_context = analysis_response

        output += "\n\n"
        output += f"**:red[Database name]**: {db_name}\n\n"
        output += f"**:red[Table names]**: {table_names}\n\n"
        message_placeholder.markdown(output + "▌")

        step2 = '### **Step 2: Python code generates [Database Context]**\n'
        output += step2
        output += f"**:blue[Table Schemas]**: {table_schemas}\n\n"
        db_system_prompt = [
            {"role": "system", "content": load_prompt("sql_gen_template").format(db_context_value=table_schemas,
                                                                                 analysis_context_value=analysis_context)},
            {"role": "user", "content": prompt},
        ]

        # full_response += str(db_system_prompt)
        # full_response += "\n\n"
        # message_placeholder.markdown(full_response)

        query_response = ''
        for response in azure.azure_ask(db_system_prompt):
            query_response += response
        json_response = json.loads(query_response)  # db查询的结果
        sql = json_response.get('response').get('sqlQueries')


        output += "\n\n"
        step3 = '### **Step 3: Query prompt generates SQL based on [Database Context] and [Analysis Context]**\n'
        output += step3

        output += f"**:blue[SQL]**: {sql[0]}\n\n"
        message_placeholder.markdown(output )

        sql_result = channel.ask_database(sql[0])

        # output += f"**:blue[SQL Result]**: {sql_result}\n\n"

        step4 = '### ** Step 4: Display query result with text and table**\n'
        output += step4
        output += f"**:blue[SQL RESULT]**:\n\n"
        message_placeholder.markdown(output)

        message_placeholder_chart.table(sql_result)


        # output += query_response
        # message_placeholder.markdown(output + "▌")
    # st.session_state.messages.append({"role": "assistant", "content": full_response})
