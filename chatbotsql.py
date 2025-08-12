# initial imports

import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# steamlit setup
st.set_page_config(page_title="Langchain chat with sql db", page_icon="&")
st.title("Langchain chat with sql db")


LOCALDB = "USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt = ["use SQL ite3 database - studebt db", "Connect to SQL database"]
selected_option = st.sidebar.radio(label = "Choose the DB", options=radio_opt)

if radio_opt.index(selected_option) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide Mysql host")
    mysql_user = st.sidebar.text_input("Mysql user")
    mysql_password = st.sidebar.text_input("Mysql pasword", type="password")
    mysql_db = st.sidebar.text_input("Mysql database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq api key", type="password")

if not db_uri:
    st.info("please enter the db information")

# llm model
llm = ChatGroq(groq_api_key = api_key, model_name = "llama3-8b-8192", streaming=True)

#db confugure
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password = None, my_sqldb = None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode = ro", uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("please provide all mysql connection details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    
if db_uri == MYSQL:
    db = configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db = configure_db(db_uri)

#Tool kit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "asssitant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="ask anything from the db")

if user_query:
    st.session_state.messages.append({"role":"user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant", "content": response})
        st.write(response)