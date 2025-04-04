from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
import asyncio
import os
from dotenv import load_dotenv

import streamlit as st
from threading import Thread

# Variables d'environnement
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Chargement des données
import pandas as pd


def load_data():
    df_customers = pd.read_csv("./data/customers.csv")
    df_orders = pd.read_csv("./data/orders.csv")
    return df_customers, df_orders


if "df_customers" not in st.session_state or "df_orders" not in st.session_state:
    st.session_state.df_customers, st.session_state.df_orders = load_data()
df_customers, df_orders = st.session_state.df_customers, st.session_state.df_orders

# Configuration du modèle et des embeddings
if "llm" not in st.session_state:
    st.session_state.llm = Gemini(
        model="models/gemini-1.5-flash", api_key=GOOGLE_API_KEY
    )
llm = Settings.llm = st.session_state.llm


# Créations des outils pour l'agent
def is_customer(customer_number: str) -> str:
    """
    A function to test the customer number of the client. It allows to know if the customer number is valid.
    Args :
        customer_number : str (the customer number)
    Returns:
        boolean

    Example :
        is_customer("AXIKB") -> True
        is_customer("ACBTP") -> False
    """
    global df_customers
    return customer_number in df_customers["customer_number"].values


def get_customer_name(customer_number: str) -> str:
    """
    A function to get the name of the customer to greet him or her.
    Args :
        customer_number : str (the customer number)
    Returns:
        string : the first name and last name of the customer

    Example :
        get_customer_name("AXIKB") -> 'Prénom : Kimberly, Nom : Fischer'
    """
    global df_customers
    infos = (
        df_customers[df_customers["customer_number"] == customer_number]["name"]
        .iloc[0]
        .split()
    )
    return f"Prénom : {infos[0]}, Nom : {infos[1]}"


def get_customer_orders(customer_number: str) -> str:
    """
    A function to get the list of the customer's orders history.
    You can use it to get the order number from a date, or an amount.
    You can use it to know all the orders regarding a status, for example.
    Args :
        customer_number : str (the customer number)
    Returns:
        string : the list of commands history (order_number, order_date, amount in euros, order_status, status_date meaning when the status changed for the last time)

    Example :
        get_customer_orders("AXIKB")
        ->
        order_number : GWUA2, order_date : 2024-12-28, amount : 954, order_status : shipped, status_date : 2025-01-06
        order_number : BTCA5, order_date : 2025-01-11, amount : 243, order_status : shipped, status_date : 2025-01-12
        …
    """
    global df_orders
    cols = ["order_number", "order_date", "amount", "order_status", "status_date"]
    results = ""
    for row in (
        df_orders[df_orders["customer_number"] == customer_number]
        .sort_values("order_date")
        .iterrows()
    ):
        for col in cols:
            results += f"{col} : {row[1][col]}, "
        results = results[:-2] + "\n"
    return results


def get_order_infos(order_number: str, customer_number: str) -> str:
    """
    A function to get the infos regarding an order from a customer
    Args :
        order_number : str (the order number)
        customer_number : str (the customer number)
    Returns:
        string : the infos of the command (order date, amount, status, date of the change of status like expedition date)

    Example :
        get_order_infos("GWUA2", "AXIKB")
        ->
        date : 2024-12-28, amount : 954, status : shipped, status changed on : 2025-01-06
    """
    global df_orders
    infos = df_orders[
        (df_orders["customer_number"] == customer_number)
        & (df_orders["order_number"] == order_number)
    ]
    if infos.shape[0] > 0:
        infos = infos.values[0][2:]
        return f"date : {infos[0]}, amount : {infos[1]}, status : {infos[2]}, status changed on : {infos[3]}"
    else:
        return "Order not found"


# Création de l'agent
system_prompt = """
Tu es un agent spécialisé dans la gestion des commandes.
Tu peux répondre à des questions concernant l'état des commandes que te pose le client.
Pour cela, tu peux utiliser différents outils.
Avant de répondre à une question, assure-toi de connaître le numéro de client du client.
Tu ne peux répondre qu'à des questions concernant les commandes du client à partir de son numéro.
Assure-toi de connaître le numéro de client (customer number) avant de répondre aux questions du client.
"""

if "agent" not in st.session_state:
    st.session_state.agent = AgentWorkflow.from_tools_or_functions(
        [is_customer, get_customer_name, get_customer_orders, get_order_infos],
        system_prompt=system_prompt,
    )
    st.session_state.ctx = Context(st.session_state.agent)

# Streamlit App
st.set_page_config(layout="wide", page_title="Agent de gestion de commandes")
st.title("Agent de gestion de commandes")


# Gestion des boucles asyncio
def get_event_loop():
    return asyncio.new_event_loop()


if "event_loop" not in st.session_state:
    st.session_state.event_loop = get_event_loop()

# with st.sidebar:
#     customer_number = st.selectbox(
#         "Numéro de client", list(df_customers["customer_number"])
#     )
#     st.dataframe(df_orders[df_orders["customer_number"] == customer_number])


# Programme principal
async def main():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bienvenue dans le chat. Comment puis-je vous aider ?",
            }
        ]
    messages = st.session_state.messages

    messages_window = st.container(height=300)
    for message in messages:
        with messages_window.chat_message(message["role"]):
            st.markdown(message["content"])

    if question := st.chat_input():
        with messages_window.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Traitement de votre requête..."):
            response = await st.session_state.agent.run(
                question, ctx=st.session_state.ctx
            )
            with messages_window.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


with st.expander("Affichage des données", expanded=True):
    customer_number = st.selectbox(
        "Numéro de client", list(df_customers["customer_number"])
    )
    st.dataframe(df_orders[df_orders["customer_number"] == customer_number])

if __name__ == "__main__":
    st.session_state.event_loop.run_until_complete(main())
