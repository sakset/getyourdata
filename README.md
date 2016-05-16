# Get your data

[![Build Status](https://travis-ci.org/sakset/getyourdata.svg?branch=master)](https://travis-ci.org/sakset/getyourdata)

### Deviympäristön asennus ###

Asenna ainakin seuraavat, käytössä PostgreSQL-kanta

    sudo apt-get install libpq-dev python-dev postgresql postgresql-contrib python-virtualenv

Mene prjojektikansioon. Asenna virtualenv-kansio projektikansion sisään. Tämän niminen kansio on gitignoressa.

    cd getyourdata/getyourdata/
    virtualenv env

Projektikansioon ilmestyi kansio nimeltä env. Aktivoi ympäristö.
    
    source env/bin/activate

Päivitä pip ja asenna requirements.txt -tiedoston sisältö.

    pip install --upgrade pip
    pip install -r requirements.txt

Jos olet asentanut pipillä uusia paketteja, lisää ne requirementseihin seuraavasti.

    pip freeze > requirements.txt

Suorita skripti devikannan (PostgreSQL) luomiseen/resetointiin.

    sudo bash create_dev_db.bash

Aja migraatiot uuteen/muuttuneeseen kantaan.

    python dev_manage.py migrate

Luo pääkäyttäjä Djangon admin-käyttöliittymää varten.

    python dev_manage.py createsuperuser

Käynnistä devipalvelin (defaulttina on portti 8000, tässä käytössä portti 8080).

    python dev_manage.py runserver 8080

Avaa selain http://localhost:8080

