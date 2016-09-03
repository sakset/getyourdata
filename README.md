# Get your data

[![Build Status](https://travis-ci.org/sakset/getyourdata.svg?branch=master)](https://travis-ci.org/sakset/getyourdata)
[![Code Climate](https://codeclimate.com/github/sakset/getyourdata/badges/gpa.svg)](https://codeclimate.com/github/sakset/getyourdata)
[![Test Coverage](https://codeclimate.com/github/sakset/getyourdata/badges/coverage.svg)](https://codeclimate.com/github/sakset/getyourdata/coverage)

### Description ###

GetYourData.org is a semi-crowdsourced site that makes it possible for a single individual to send an information request to a company. The user can select a list of companies that have information of the person, allowing every information request to be created at once. Depending on the organization, a request can be handled using either an email message (automatically sent by GetYourData.org) or in mail (printable letter is created by GetYourData.org).

More information can be found at [requestyourdata.org](http://okffi.github.io/ryd/)

### Setting up the development server ###

Install the required dependencies using the following command (should work on Debian and derivatives such as Ubuntu)

    sudo apt-get install libpq-dev libjpeg-dev python-dev postgresql postgresql-contrib python-virtualenv memcached

Navigate to the project directory. Install virtualenv.

    cd getyourdata/getyourdata/
    virtualenv env

Enable the now installed virtualenv. This will help keep the project-related Python configuration and installation separate from the system-wide Python installation.
    
    source env/bin/activate

Upgrade pip and install dependencies in the requirements.txt file.

    pip install --upgrade pip
    pip install -r requirements.txt

If you've installed new packages, update requirements.txt to include the new dependencies.

    pip freeze > requirements.txt

Run a script to create/flush the development database (PostgreSQL).

    sudo bash create_dev_db.bash

Run the database migrations.

    python dev_manage.py migrate

Create a superuser to use the admin interface at /admin/.

    python dev_manage.py createsuperuser

Start the development server (default port is 8000, the following example uses 8080).

    python dev_manage.py runserver 8080

Open the browser at http://localhost:8080

That's it!

