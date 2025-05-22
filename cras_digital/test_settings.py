from .settings import *  # noqa: F403, F401

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cras_db',
        'USER': 'cras_user',
        'PASSWORD': 'cras_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_cras_db',
        },
    }
}

TEST_DATABASE_CREATE = False
