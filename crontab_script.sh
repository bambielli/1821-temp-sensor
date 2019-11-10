#!/bin/bash
. /home/pi/.bash_profile
cd /home/pi/1821-temp-sensor
export PATH=/usr/local/bin:$PATH
pipenv run python airtable_temperatures.py
