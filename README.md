# Agent de gestion de commandes

Ce petit projet permet d'utiliser un **agent conversationnel** capable de répondre aux clients fictifs concernant leurs commandes fictives.

Il s'appuie sur **LlamaIndex** pour répondre aux questions des "clients", avec un agent disposant de quatre fonctions retrouvant les informations de commande.

Il utilise aussi Gemeni 1.5 Flash comme LLM et base de l'agent.

Le programme utilise deux dataframes au format csv :
**customers.csv** : contient les données de clients (customer_number et customer_name)
**orders.csv** : contient les données des commandes (order_number,	customer_number,	order_date,	amount,	order_status,	status_date)
Ces fichiers se trouvent dans le dossier data, mais peuvent être recréés à l'aide du Notebook test_agent.ipynb qui affiche également le contenu des deux DataFrames.

