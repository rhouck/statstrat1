# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'market',                      
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': ''
    }
}


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# set environment variables
# do not add to repo
import os

os.environ['SECRET_KEY'] = '_0zruahjm4c%5nw20!jp69+p9lbrckn!lu75(knwr(i8gh8g(2'