# Agent de gestion de commandes

## Présentation

Ce petit projet permet d'utiliser un **agent conversationnel** capable de répondre aux clients fictifs concernant leurs commandes fictives.

Il s'appuie sur **LlamaIndex** pour répondre aux questions des "clients", avec un agent disposant de quatre fonctions retrouvant les informations de commande.

Il utilise aussi Gemeni 1.5 Flash comme LLM et base de l'agent.

Le programme utilise deux dataframes au format csv :

**customers.csv** : contient les données de clients (customer_number et customer_name)

**orders.csv** : contient les données des commandes (order_number,	customer_number,	order_date,	amount,	order_status,	status_date)

Ces fichiers se trouvent dans le dossier data, mais peuvent être recréés à l'aide du Notebook test_agent.ipynb qui affiche également le contenu des deux DataFrames.

## GOOGLE API KEY

Pour utiliser cette appli, vous devez entrer votre clef API Google dans le fichier .env

Vous pouvez utiliser le fichier .env_to_create comme modèle afin de respecter le nom de la variable globale ou entrer : 

GOOGLE_API_KEY = 'YOUR_API_KEY'

## Version CLI

Le programme agent.py contient la première version en ligne de commande

**Utilisation** : python agent.py

## Version Streamlit

Le programme main.py contient l'appli Streamlit mise à jour

**Utilisation** : python streamlit run main.py

Je conseille d'utiliser "python" dans la ligne de commande pour éviter tout problème avec la gestion de l'environnement virtuel.

L'application affiche la liste des numéros de client et l'historique des commandes pour tester le chatbot.
