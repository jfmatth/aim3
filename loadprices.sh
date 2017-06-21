#!/bin/bash
# this runs once per hour, so assume it's sometime in the 9th hour

# Run this at 4pm PST, this gear is EST
if [ $(date +%H) == 18 ]; then 
	cd $OPENSHIFT_REPO_DIR
	python manage.py loadprices
	python manage.py advice	
 fi