from .settings import *

DEBUG = True

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'getyourdatadevdb',
    'USER': 'getyourdatadevuser',
    'PASSWORD': 'getyourdatadevpwd',
    'HOST': 'localhost',
    'PORT': '',
    }
}

AUTH_PASSWORD_VALIDATORS = []
