# Installation instructions

## Add superuser
Login to console and run 

    python manage.py createsuperuser

## Setup AllAuth providers
http://django-allauth.readthedocs.io/en/latest/installation.html#post-installation

### Add Github oAuth https://github.com/settings/developers
#### RUNSERVER (local)
    Client ID
    cae35f4c53370ee08987
    Client Secret
    ec1704e71c0a08d4dd6098898d9252666374e26b
#### MINISHIFT (local)
    Client ID
    c2724e8ce0569cb4387e
    Client Secret
    7db8af62f5acbeafbf90aaa072e58612b6cf5d99

## Setup which exchanges to load
Add NYSE, AMEX and NASDAQ to Loader.Exchange

## Load some stock history
### setup for FTP settings
    ftplogin.bat
    python manage.py loadhistory <date>

