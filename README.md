# projetbts

Projet BTS django

# Utilisation du git

```bash
ssh-keygen # Ajouter la clé publique ssh à votre profil

# Cloner le repo
git clone git@github.com:Ap4sh/projetbts.git

# Pull les changements si il y en a eu (important à faire avant de commencer à dév ou push ou quoi)
git pull origin main

# Une fois que vous avez fait des changements, ajouter des fichiers etc vous pouvez faire:
git add fichier # ou alors git add . (pour ajouter tout le dossier entier)

# une fois le git add réalisé, il faut commit avec une raison
git commit -m "raison"

# push le commit sur la branche main
git push -u origin main

# si vs avez un pb dites moi
```


# theorie

Partie BDD
![bdd](https://i.imgur.com/5lS7Yyw.png)

Diagramme de gantt
![gantt](https://i.imgur.com/eJyT9hq.png)


Objectif du projet : faire une application permettant aux utilisateurs de consulter les données météorologiques de leurs régions

Échéance de livraison : 15 avril

Chantiers et livrables attendus : Le premier livrable attendu est un PMP, un dossier comprenant notre diagramme de gantt, notre organigramme complet etc.. Puis, enfin, l'application en elle-même.

Plan de charge : 70 jours au total 



Niveau application, on veut prendre exemple là-dessus https://www.meteoetradar.com/ - le but c'est de faire une application simple dans ce style avec une première page qui affiche la carte de France avec les infos de base de quleques villes etc, une partie utilisateur avec un login et une partie "alerte" le but c'est que toutes les heures ou quoi on check si l'API donne une alerte météo pour la France, on prend la localisation et le type d'alerte et si l'utilisateur est concerné, pendant le login on check et on lui envoie l'alerte. Ptetre qu'on fera une alerte par mail un jour
On veut faire deux dockers un avec mysql et un avec django, ptetre pas UV/poetry et juste un env python basique ou quoi

https://github.com/kshitizrohilla/weather-app-using-openweathermap-api/
https://kshitiz.me/weather-app-using-openweathermap-api/

ça c'est stylé et ça utilise l'api gratos openweather donc on peut prendre exemple pour l'utilisation de l'api openweather c'est propre, sinon globalement sur github ya des tonnes de projets/d'exmples d'app météo et tout en django qui font comme nous
https://github.com/dimasyotama/django-weather-app
https://github.com/akrish4/Django-Weather-Web-App

# Installation et lancement

## Installation

1. cloner le projet etc (voir + haut)
```bash
git clone git@github.com:Ap4sh/projetbts.git
cd projetbts
```

2. faire le fichier env
```bash
cp .env.example .env
```

3. docker de base
```bash
# stop les contenurs qui tournent
docker-compose down -v

# build les imgs
docker-compose build

# start conteneur
docker-compose up -d
```

4. faire superuser django
```bash
docker-compose exec web python manage.py createsuperuser
```

## Utilisation

1. app :
- user : http://localhost:8000
- admin : http://localhost:8000/admin

2. pour stop l'app :
```bash
docker-compose down
```

## Cmd utiles

Quelques commandes utiles :

```bash
# logs docker
docker-compose logs -f

# redem docker
docker-compose restart web

# exec des cmd DANS le docker
docker-compose exec web python manage.py [commande]

# cree une migr
docker-compose exec web python manage.py makemigrations

# appliquer migr
docker-compose exec web python manage.py migrate
```

## Structure du projet
```
projetbts/
├── meteo/              # cfg django
├── weather/            # app meteo
├── templates/          # template globaux
├── static/             # static? ta mere si tu me demandes c quoi
├── manage.py          # scr gestion django
├── Dockerfile         # cfg docker
└── docker-compose.yml # cfg docker compose (oui oui)
```

Atm rien de "vraiment" fonctionnel mais au moins on pose les bases et maintenant chacun peut dév sa partie tranquille.

