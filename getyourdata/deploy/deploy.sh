#!/bin/bash
# A script that (re)deploys the site by cloning the latest version of the web application
# from GitHub and deploying it
cd getyourdata;

echo "Cloning the latest version...";
# This also wipes out all local changes and virtualenv
git fetch --all;
git reset --hard origin/master;
cp ../secrets.py getyourdata/getyourdata/secrets.py;

echo "Starting virtualenv...";
virtualenv env;
source env/bin/activate;
cd getyourdata;

echo "Installing dependencies and running migrations...";
pip install -r requirements.txt;
python manage.py makemigrations flatpages --noinput;
python manage.py migrate --noinput;
python manage.py collectstatic --noinput;
python manage.py update_translation_fields;

echo "Restarting uWSGI..."
touch /tmp/getyourdata-restart;
