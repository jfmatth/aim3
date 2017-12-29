#!/bin/bash
# this runs once per hour, so assume it's sometime in the 9th hour

echo "executing loadprices.sh..."
# Run this at 4pm PST, this gear is EST
if [ $(date +%H) == 19 ]; then 
        cd /home/django
        source vpython3/bin/activate
        cd mysite
	echo "running manage.py loadprices"
	python manage.py loadprices
	python manage.py advice	
 fi
