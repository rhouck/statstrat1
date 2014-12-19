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

os.environ['SECRET_KEY'] = 'y@v+#r3vt3kh7&hj2%y7pjcx4&x0_rcz8^l6y4-@wo4qq+fx@='