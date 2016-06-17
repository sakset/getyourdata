# Development server documentation
The following applies to the development server running at okffi-dev1.kapsi.fi

### Installed software ###
The development server uses
* nginx (a web server, serves requests using uWSGI)
* uWSGI (an application server, responsible for handling web application workers)
* PostgreSQL (database server)
* virtualenv (virtualized environment used to run the web application in isolation from the system-wide Python installation)
* pip (package manager for Python)
* memcached (memory caching system)

The dependencies can be installed in Debian-based distros with the following command:

    sudo apt-get install libjpeg-dev python-virtualenv python-pip libpq-dev memcached apache2-utils
    
### Configuration files ###

**/etc/uwsgi/vassals/getyourdata_uwsgi.ini**

Used by uWSGI in vassal mode to handle web application workers. When nginx receives a HTTP request, the request is redirected to one of the free workers using an UNIX socket. 

The actual web application workers run with the GID and UID defined below. 

When /tmp/getyourdata-restart is touched, uWSGI will reload the workers; this is done when we need to switch to a newer version of the web application on the fly.

The following example assumes the virtualenv is in the path /home/USER/getyourdata/env.

    [uwsgi]
    chdir = /home/USER/getyourdata/getyourdata
    module = getyourdata.wsgi
    home = /home/USER/getyourdata/env
    
    master = true
    processes = 5
    socket = /home/USER/getyourdata/getyourdata/getyourdata.sock
    
    uid = USER
    gid = USER
    
    # If possible, you could also use 644
    chmod-socket = 666
    vacuum = true
    
    # When /tmp/getyourdata-reload is modified by any user, the web application is reloaded
    touch-reload=/tmp/getyourdata-restart
    
    logto = /var/log/getyourdata.log
    
**/etc/nginx/sites-enabled/getyourdata.conf**

nginx connects to the uWSGI application server through an UNIX socket using the WSGI protocol. Static files are served from a local directory. [ngx_http_auth_basic](http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html) is used for authentication.

uwsgi_params referred to in 'location /' is the [file described here](http://uwsgi-docs.readthedocs.io/en/latest/Nginx.html#what-is-the-uwsgi-params-file).

    upstream django_getyourdata {
           server unix:///home/USER/getyourdata/getyourdata/getyourdata.sock;
    }
    
    server {
           listen 80;
    
           server_name okffi-dev1.kapsi.fi;
           charset utf-8;
    
           client_max_body_size 5M;
    
           location /static {
                   alias /home/USER/static/getyourdata;
           }
    
           location / {
                   uwsgi_pass django_getyourdata;
                   include /home/USER/getyourdata/getyourdata/uwsgi_params;
		   auth_basic "Restricted";
		   auth_basic_user_file /etc/nginx/sites_enabled/getyourdata.htpasswd;
           }
    }
    
**/etc/init/uwsgi.conf**

An [Upstart](http://upstart.ubuntu.com/) service file. 

```
    description "uWSGI instance"
    start on runlevel [2345]
    stop on runlevel [06]
    
    respawn
    
    exec uwsgi --emperor /etc/uwsgi/vassals --logto /var/log/uwsgi.log
```

With it the uWSGI application server service can be managed using the following commands:

```
    restart uwsgi
    start uwsgi
    stop uwsgi
```

**Deployment script deploy.sh**

The script is run by the same user running the web application. It is meant to be run automatically in response to a successful commit on the master branch, making it a part of the *continuous integration* workflow.

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
    python manage.py migrate --noinput;
    python manage.py collectstatic --noinput;
    
    echo "Restarting uWSGI..."
    touch /tmp/getyourdata-restart;
