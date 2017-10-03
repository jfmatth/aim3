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


# Conversion commands
## Remove old symbols and their prices
Login to the django pod
```
from aim.models import Symbol
Symbol.objects.filter(currentprice__isnull=True).delete()
```
## Remove all symbols that don't have current prices, by year
```
Symbol.objects.filter(currentprice__date__year=2014).delete()
Symbol.objects.filter(currentprice__date__year=2015).delete()
Symbol.objects.filter(currentprice__date__year=2016).delete()
```
### Now do it for all months until the conversion month (Sept)
```
Symbol.objects.filter(currentprice__date__month=1).delete()
Symbol.objects.filter(currentprice__date__month=2).delete()
Symbol.objects.filter(currentprice__date__month=3).delete()
Symbol.objects.filter(currentprice__date__month=4).delete()
Symbol.objects.filter(currentprice__date__month=5).delete()
Symbol.objects.filter(currentprice__date__month=6).delete()
Symbol.objects.filter(currentprice__date__month=7).delete()
Symbol.objects.filter(currentprice__date__month=8).delete()
```

## Limit how many years of price history we have, except for holdings we already have
```
>>> for h in Holding.objects.all():
...   try:
...     h.transaction_set.all().order_by('date')[0]
...   except:
...     pass
...
<Transaction: [UTES in Testing] [2016-11-02] (Buy - .t33.000 @ 29.733)>
<Transaction: [CURE in John - IRA 682] [2013-03-05] (Buy - .t104.000 @ 71.970)>
<Transaction: [LABU in Danica - IRA] [2015-06-02] (Buy - .t174.000 @ 41.020)>
<Transaction: [INDL in John - IRA 682] [2013-01-09] (Buy - .t482.000 @ 20.730)>
<Transaction: [RETL in Testing] [2017-01-05] (Buy - .t100.000 @ 36.016)>
<Transaction: [VMW in Testing] [2016-10-07] (Buy - .t90.000 @ 74.300)>
<Transaction: [SPXL in John - IRA 682] [2012-01-20] (Buy - .t150.000 @ 69.570)>
<Transaction: [TNA in John - IRA 682] [2015-08-27] (Buy - .t151.000 @ 66.290)>
<Transaction: [DZK in Danica - IRA] [2011-08-10] (Buy - .t116.000 @ 42.900)>
<Transaction: [NUGT in John - IRA 682] [2016-08-02] (Buy - .t30.000 @ 173.190)>
<Transaction: [KNOW in John - IRA 682] [2013-07-29] (Buy - .t210.000 @ 51.920)>
<Transaction: [DZK in Thomas - IRA 684] [2011-08-10] (Buy - .t69.000 @ 43.260)>
<Transaction: [DZK in John - IRA 682] [2010-05-07] (Buy - .t100.000 @ 51.380)>
<Transaction: [SPXL in Danica - IRA] [2015-09-21] (Buy - .t85.000 @ 74.970)>
<Transaction: [TNA in Danica - IRA] [2014-02-03] (Buy - .t125.000 @ 63.878)>
<Transaction: [DRN in John - IRA 682] [2011-08-09] (Buy - .t250.000 @ 41.410)>
<Transaction: [FAS in John - IRA 682] [2011-12-05] (Buy - .t150.000 @ 67.020)>
<Transaction: [LABU in John - IRA 682] [2016-06-07] (Buy - .t290.000 @ 37.030)>
<Transaction: [TECL in John - IRA 682] [2011-01-15] (Buy - .t200.000 @ 50.040)>
<Transaction: [RUSL in Thomas - IRA 684] [2014-05-09] (Buy - .t330.000 @ 15.160)>
<Transaction: [MIDU in John - IRA 682] [2015-09-16] (Buy - .t1000.000 @ 22.430)>
>>> 
```

## remove all prices from 2009
```
Price.objects.filter(date__year=2009).delete()
```
## for starter migration, remove all prices except those that are in current holdings
### this query takes A WHILE locally on battery :)
```
Symbol.objects.filter(holding__isnull=True).count()
8422
Symbol.objects.filter(holding__isnull=True).delete()
```
## then dumpdata w/o certain apps and load in to starter DB
```
python manage.py dumpdata --indent=2 --exclude loader > all.json
python manage.py loaddata all.json
```
