"""Constant definition for pyknmi."""

""" Examples of URLs
    Current Data: http://weerlive.nl/api/json-data-10min.php?key=demo&locatie=52.0910879,5.1124231
    Forecast Data: https://data.meteoserver.nl/api/uurverwachting_gfs.php?locatie=Utrecht&key=342b7e36ac
"""

FORECAST_BASE_URL = "https://data.meteoserver.nl/api/uurverwachting_gfs.php"
LIVE_BASE_URL = "http://weerlive.nl/api/json-data-10min.php"

DEFAULT_TIMEOUT = 10