""" The test for the API """
"""Run an example script to quickly test."""
import asyncio
import logging
import time
import json

from pyknmi.client import KnmiData
from pyknmi.errors import KnmiError

_LOGGER = logging.getLogger(__name__)

LATITUDE = 52.0910879
LONGITUDE = 5.1124231

async def main() -> None:
    """Create the aiohttp session and run the example."""

    # Get the API Key from secrets.json
    path_index = __file__.rfind("/")
    top_path = __file__[0:path_index]
    filepath = f"{top_path}/secrets.json"
    with open(filepath) as json_file:
        data = json.load(json_file)
        api_key = data["connection"]["api_key"]

    logging.basicConfig(level=logging.DEBUG)

    knmi = KnmiData(api_key, LATITUDE, LONGITUDE)

    start = time.time()

    try:

        _LOGGER.info("GETTING CURRENT DATA:")
        data = await knmi.current_data()
        print(json.dumps(data, indent=1))
        # for row in data:
        #     _LOGGER.info(f"{row.beaufort_value} - {row.beaufort_text} - {row.city_name} - {row.wind_cdir} - {row.wind_dir} - {row.ob_time} - {row.obs_time_local} - {row.timezone} - {row.sunrise} - {row.slp}")


    except KnmiError as err:
        _LOGGER.info(err)

    end = time.time()

    _LOGGER.info("Execution time: %s seconds", end - start)


asyncio.run(main())
