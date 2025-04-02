from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
import asyncio
import os
from dotenv import load_dotenv

# Variables d'environnement
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Chargement des données
print("Chargement de la base de données…")
import pandas as pd

df_customers = pd.read_csv("./data/customers.csv")
df_orders = pd.read_csv("./data/orders.csv")

# Configuration du modèle et des embeddings
llm = Gemini(model="models/gemini-1.5-flash", api_key=GOOGLE_API_KEY)

Settings.llm = llm


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
    Args :
        customer_number : str (the customer number)
    Returns:
        string : the list of commands history

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

agent = AgentWorkflow.from_tools_or_functions(
    [is_customer, get_customer_name, get_customer_orders, get_order_infos],
    system_prompt=system_prompt,
)
ctx = Context(agent)


async def main():
    global agent, ctx
    print("Bienvenue dans le chat. Entrez quit ou exit pour quitter le programme")
    while True:
        question = input("> : ")
        if question.strip().lower() in ["quit", "exit"]:
            break
        response = await agent.run(question, ctx=ctx)
        print(str(response))


if __name__ == "__main__":
    asyncio.run(main())
