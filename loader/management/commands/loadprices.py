from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.sites.models import Site

import logging
import csv
import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
from ftplib import FTP
from io import BytesIO

from aim.models import Symbol, Price
from loader.models import Exchange, ExchangePrice, PriceError

# Get an instance of a logger
logger = logging.getLogger(__name__)


def EODDATA_loader(loaddate, history):
    """
    EODDATA_loader - this function downloads the latest exchange list for each list in Exchange(s), then downloads the prices
    for today into ExchangePrice.
        
    """

    # Make sure we have our environment variabels.
    if not settings.FTPLOGIN:
        logger.info("no FTPLOGIN in settings")
        return

    # Load todays prices from FTP EODDATA.com

    logger.info("EODDATA_loader() start")

    datestr = loaddate.strftime("%Y%m%d")
    logger.info("Getting ready to load Exchanges / Prices for %s" % datestr)

    ftp = FTP("ftp.eoddata.com")
    try:
        logger.debug("FTP Login as %s" % settings.FTPLOGIN)
        ftp.login(settings.FTPLOGIN, settings.FTPPASS)
    except:
        logger.debug("Error logging into FTP")

    # loop over all Indexes, grabbing the latest exchange and then loading the prices we need.
    ftp.cwd("Names")
    for e in Exchange.objects.all():
        mfile = BytesIO()

        try:
            exchangefile = "%s.txt" % e.name

            logger.debug("Retreiving Exchange %s" % exchangefile)

            ftp.retrbinary("RETR %s" % exchangefile, mfile.write)

            e.data = mfile.getvalue()
            e.loaded = False
            e.save()

            logger.debug("%s retrieved and saved" % exchangefile)

        except:
            logger.debug("Current datetime = $s, Error retreiving index %s" % (datetime.datetime.today(), e.name))

        del (mfile)

    if history:
        ftp.cwd("/History")
    else:
        ftp.cwd("/")

    for e in Exchange.objects.all():
        mfile = BytesIO()
        try:
            pricefile = "%s_%s.txt" % (e.name, datestr)

            logger.debug("Retreiving prices Exchange %s" % pricefile)

            ftp.retrbinary("RETR %s" % pricefile, mfile.write)

            p = ExchangePrice(exchange=e, data=mfile.getvalue(), loaded=False)
            p.save()

            logger.debug("%s Prices Saved" % pricefile)
        except:
            logger.debug("error retreiving %s" % pricefile)

        del (mfile)

    logger.debug("ftp quit")
    ftp.quit()

    ftp = None
    mfile = None
    p = None

    logger.info("EODDATA_loader() complete")


def ProcessExchange(f):
    """
    ProcessExchange - Given a string (typcically the text from EODDATA for an Exchange file, import them into the Symbols list )
    """

    logger.info("ProcessExchange() start")

    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    header = reader.__next__()

    if not header[0] == "Symbol" or not header[1] == "Name":
        raise Exception("Error - Header line in %s looks wrong" % header)

    try:
        for csvline in reader:
            logger.debug("processing %s" % csvline)
            s, created = Symbol.objects.get_or_create(name=csvline[0], defaults={"description": csvline[1]})
            if created:
                logger.debug("Created")
    except:
        raise 
        logger.debug("Error loading %s" % csvline)

    logger.info("ProcessExchange() complete")


def LoadExchange():
    """
    LoadExchange - Gets all the records in Exchange that haven't been loaded, and process' them into the Symbols table.
    """

    logger.info("LoadExchange() start")

    count = 0

    for e in Exchange.objects.filter(loaded=False):
        # we have an exchange that hasn't been loaded.

        # sniff it out and load it into Symbols.
        # ProcessExchange(StringIO.StringIO(e.data))
        ProcessExchange(StringIO(e.data))

        e.loaded = True
        e.save()

        count += 1

    logger.info("LoadExchange() complete")

    return count


@transaction.atomic
def ProcessPrices(f, headers=False):
    """
    Given a string F, Import a file f into the prices table.
    """

    logger.info("ProcessPrices() start")

    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if headers:
        header = reader.next()

        if not header[0] == "Symbol" or not header[1] == "Date":
            raise Exception("Error - Header line in looks wrong, %s" % header)

    # add import improvement. 
    datecheck = None
    count = 0

    logger.info("Start processing prices ...")
    for csvline in reader:

        d = datetime.datetime.strptime(csvline[1], "%Y%m%d").date()

        if not datecheck == d:
            # this is the date we are checking, so load all symbols from price for 
            # this date and use it for quick checking.
            logger.debug("datecheck = %s" % d)
            datecheck = d

            symbollist = set(Price.objects.filter(date=d).values_list("symbol__name", flat=True))
            logger.debug("sybollist populated")

        # now use the symbollist to verify each CSV line w/o a lookup
        if csvline[0] in symbollist:
            # if we already have it here, then skip.
            logger.debug("skipping %s due to duplicate" % csvline[0])
            pass
        else:

            try:
                sym = Symbol.objects.get(name=csvline[0])
                p = Price()
                p.symbol = sym
                p.date = d
                p.high = csvline[3]
                p.low = csvline[4]
                p.close = csvline[5]
                p.volume = csvline[6]
                p.save()

                count += 1

            except ObjectDoesNotExist:
                # add this to the price error if necessary
                p, c = PriceError.objects.get_or_create(symbolname=csvline[0])

    logger.info("ProcessPrices() complete")

    reader = None
    symbollist = None

    return count


def LoadPrices():
    """
    Gets all ExchangePrice records that haven't been loaded, and processes them.
    """
    logger.info("LoadPrices() start")

    count = 0

    for e in ExchangePrice.objects.filter(loaded=False):
        # we have an exchange that hasn't been loaded.

        # sniff it out and load it into Symbols.
        n = ProcessPrices(StringIO(e.data))
        e.loaded = True
        e.save()

        count += n

    logger.info("LoadPrices() complete")

    return count


def NotifyAdmin(subject, body):
    if not settings.EMAIL_HOST_USER:
        logger.info("NotifyAdmin - No EMAILHOST specified in settings")
        return

    mail_admins(subject, body)


def LoadAll(date=None, history=False):
    """
    This runs through the daily routine to download the prices via FTP from EODDATA and then load them into the Symbol and Prices tables.
    """

    logger.info("LoadAll() Start")

    loaddate = date or datetime.datetime.today()

    if loaddate.weekday() >= 0 and loaddate.weekday() < 5:
        EODDATA_loader(loaddate, history)
        c1 = LoadExchange()
        c2 = LoadPrices()

        cs = Site.objects.get_current()

        subject = "%s - %s Prices Loaded for %s" % (cs.domain, cs.name, loaddate)
        body = "%s Exchanges loaded, %s prices loaded" % (c1, c2)
        NotifyAdmin(subject, body)
    else:
        logger.info("Skipping weekend %s" % loaddate)


    logger.info("LoadAll() complete")

# turn this into a management command.
class Command(BaseCommand):
    args = "Date optional"
    help = "loads all stock prices for <date>"

    def handle(self, *args, **options):
        self.stdout.write("Loadprices.py - calling LoadAll()")
        LoadAll()
        self.stdout.write("Loadprices.py - Complete")
