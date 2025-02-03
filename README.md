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

Chantiers et livrables attendus : Le premier livrable attendu est un PMP, un dossier comprenant notre diagramme de gantt, notre organigramme complet etc.. Puis, enfin, l’application en elle-même.

Plan de charge : 70 jours au total 



Niveau application, on veut prendre exemple là-dessus https://www.meteoetradar.com/ - le but c'est de faire une application simple dans ce style avec une première page qui affiche la carte de France avec les infos de base de quleques villes etc, une partie utilisateur avec un login et une partie "alerte" le but c'est que toutes les heures ou quoi on check si l'API donne une alerte météo pour la France, on prend la localisation et le type d'alerte et si l'utilisateur est concerné, pendant le login on check et on lui envoie l'alerte. Ptetre qu'on fera une alerte par mail un jour
On veut faire deux dockers un avec mysql et un avec django, ptetre pas UV/poetry et juste un env python basique ou quoi
