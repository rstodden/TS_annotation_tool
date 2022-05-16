# Postgres Database in Django
- If you consider using many data or if you want to protect your database, Postgres might be an option for you.
- More infromatin is provided here:
  - https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django
  - https://docs.djangoproject.com/en/4.0/ref/databases/
  - https://www.postgresqltutorial.com/install-postgresql-linux/

## Installation
- install postgres
- enter your database credential in [./TS_annotation_tool/settings.py](./TS_annotation_tool/settings.py) and [./TS_annotation_tool/settings_deployment.py](./TS_annotation_tool/settings_deployment.py)
- set up postgres db with `sudo -u postgres psql`
  - `postgres=# create database YOUR_DATABASE_NAME with owner YOUR_USERNAME;`

## Fill database
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python3 manage.py createsuperuser`

## Run System 
- `python manage.py runserver` open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser
