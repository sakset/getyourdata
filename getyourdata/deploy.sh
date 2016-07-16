#!/bin/bash
# Script that creates the initial database, runs migrations and loads initial fixtures
# (eg. makes the site ready for launch)
echo "Creating database..."

sudo ./create_dev_db.sh
cd ..

echo "Creating virtualenv..."
# Don't create the virtualenv if it already exists
if [ ! -d "env" ]; then
    virtualenv env
fi

source env/bin/activate
cd getyourdata
pip install -r requirements.txt

echo "Running migrations..."

python manage.py makemigrations flatpages
python manage.py migrate
python manage.py update_translation_fields

echo "Collecting static files..."
python manage.py collectstatic

echo "Loading initial fixtures..."
python manage.py loaddata default_fields

echo "Done!"
