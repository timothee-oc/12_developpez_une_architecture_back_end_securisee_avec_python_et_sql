# Projet 12: Développez une architecture back-end sécurisée avec Python et SQL

Ce projet consistait à développer une application de CRM en ligne de commande pour une entreprise fictive nommée EpicEvents.

L'application doit permettre de réaliser les opérations CRUD sur des utilisateurs, des clients, des contrats et des évènements.

Il fallait également mettre en place un système d'authentification et de permissions selon des rôles correspondant à des départements.

## Installation

- git clone https://github.com/timothee-oc/12_developpez_une_architecture_back_end_securisee_avec_python_et_sql.git
- cd 12_developpez_une_architecture_back_end_securisee_avec_python_et_sql
- python -m venv venv
- .\venv\Script\activate
- pip install -r requirements.txt
- Créez un fichier `.env` sur le modèle du fichier `.env.sample`. Vous aurez besoin d'un compte Sentry pour avoir un SENTRY_DSN.

## Utilisation
Un utilisiteur a déjà été créé dans la base de données. Vous pouvez vous connecter avec ses identifiants:
- username: admin
- password: admin

Il a le rôle `management` qui lui permet de créer d'autres utilisateurs.

La première chose à faire est de s'authenfier avec :

`python epic_events.py login USERNAME PASSWORD`

La liste des commandes disponibles est accessible avec :

`python epic_events.py --help`

L'option `--help` peut également être ajoutée à n'importe quelle commande pour connaître ses arguments et options. 
