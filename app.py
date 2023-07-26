import streamlit as st
import openai
import json

from chat2db.chat.azure import Azure
from chat2db.database.channel import Channel
from chat2db.prompts import load_prompt
import chat2db.utils as U
from streamlit_echarts import st_echarts
from chat2db.chart import echarts

st.title("Query GPT")

if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": load_prompt("analysis")}
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


    for response in azure.azure_ask(st.session_state.messages):
        analysis_response += response
    json_response = json.loads(analysis_response)

    if json_response['response'].get('dbCheck') != 'Yes':
        # TODO: 不查询数据库
        pass
    else:
        print(f"response is：{json_response['response']}")
        db_name = json_response['response'].get('dbName')
        keywods = [i for i in json_response['response'].get('keywords')]
        channel = Channel(db_name)

        step1 = '### **Analysis prompt generates [Analysis Context]**\n'
        output = step1 + analysis_response

        table_names = ','.join(channel.target_tables).strip(',')
        table_schemas = channel.database_schema_string
        analysis_context = analysis_response

        output += "\n\n"
        output += f"**:red[Database name]**: {db_name}\n\n"
        output += f"**:red[Table names]**: {table_names}\n\n"
        message_placeholder.markdown(output + "▌")

        #step2 = '### **Step 2: Python code generates [Database Context]**\n'
        #output += step2
        #output += f"**:blue[Table Schemas]**: {table_schemas}\n\n"

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
        print(f"query_response is {query_response}")
        json_response = json.loads(query_response)  # db查询的结果
        sql = json_response.get('response').get('sqlQueries')


        output += "\n\n"
        step3 = '### **Query prompt generates SQL based on [Database Context] and [Analysis Context]**\n'
        output += step3

        output += f"**:blue[SQL]**: {sql[0]}\n\n"
        #message_placeholder.markdown(output )

        
        step4 = '### **Execute SQL and show result**\n'
        output += step4

        sql_result = channel.ask_database(sql[0])
        # output += f"**:blue[SQL Result]**: {sql_result}\n\n"

        #print(f"analysis context is: {analysis_context}")
        print(f"sql result is: {sql_result}")

        # calculate and print number of indicators and number of rows
        #row_count = U.count_row_number(sql_result.size)
        indicators_count = U.count_indicators(analysis_context)
        chart_type = U.get_chart_type(analysis_context)
        multi_series = U.get_multi_series(analysis_context)

        #output += f"**:red[Number of Indicators]**: {indicators_count}\n\n"
        #output += f"**:red[Number of Rows]**: {sql_result.size}\n\n"
        output += f"**:red[Chart Type]**: {chart_type}\n\n"
        output += f"**:red[Multi Series]**: {multi_series}\n\n"
        output += f"**:blue[SQL RESULT]**:\n\n"


        message_placeholder.markdown(output)

        message_placeholder_chart.table(sql_result)
        echarts.render_chart(sql_result, chart_type, multi_series)