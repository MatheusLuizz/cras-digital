@echo off
set POSTGRES_DB=cras_db
set POSTGRES_USER=cras_user
set POSTGRES_PASSWORD=cras_password
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432

coverage run manage.py test --settings=cras_digital.test_settings %*