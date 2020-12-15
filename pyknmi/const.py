"""Constant definition for pyknmi."""

""" Examples of URLs
    Current Data: http://weerlive.nl/api/json-data-10min.php?key=API_KEY&locatie=LAT,LON
    Forecast Data: https://data.meteoserver.nl/api/uurverwachting_gfs.php?locatie=LAT,LON&key=API_KEY
"""

FORECAST_BASE_URL = "https://data.meteoserver.nl/api/uurverwachting_gfs.php"
LIVE_BASE_URL = "https://data.meteoserver.nl/api/liveweer_synop.php"

DEFAULT_TIMEOUT = 10