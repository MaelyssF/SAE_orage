Création de l'environnement virtuel et lancement du venv :  
```Bash
python3 -m venv .venv
source .venv/bin/activate
```
Installer Django dans le venv et vérification de la version : 
```Bash 
pip install django
django-admin --version
```

_Rappel_ : Pour mettre à jour les traces des packages installés :  
pip freeze > requirements.txt

Pour exécuter le fichier manage.py, Il faut se placer dans 'SAE_orage/surveillanceOrages/' .   
Lancer le serveur :  
```Bash
python manage.py runserver
```

Lancer des tests :  
coverage run --source='orage' manage.py test
rapport de couverture dans le terminal : coverage report
coverage html

Dans le ".gitignore", voici un exemple des chemins pour les fichiers qui seront à ignorer :  
```Gitignore
surveillanceOrages/htmlcov/*
surveillanceOrages/db.sqlite3
surveillanceOrages/.coverage
surveillanceOrages/surveillanceOrages/__pycache__/
surveillanceOrages/orage/__pycache__/
surveillanceOrages/orage/migrations/__pycache__/
venv/
surveillanceOrages/.coverage
surveillanceOrages/.coveragerc

surveillanceOrages/orage/tests/__pycache__/*
```


Pour ajouter une application au projet Django 'surveillanceOrages' :  
```Bash
manage.py startapp orageApp
```