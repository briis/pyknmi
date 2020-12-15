"""Define a client to interact with KNMI."""
import asyncio
import sys
import logging
from typing import Optional
from datetime import datetime as dt

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from pyknmi.errors import InvalidApiKey, RequestError
from pyknmi.const import (
    LIVE_BASE_URL,
    FORECAST_BASE_URL,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

class KnmiData:
    """KNMI Data Class Handler."""

    def __init__(
        self,
        api_key: str,
        latitude: float,
        longitude: float,
        session: Optional[ClientSession] = None,
        ):
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._session: ClientSession = session
        self.req = session


    async def current_data(self) -> None:
        """Return Current Data for Location."""

        """ERIK: The below functions return data for Current Weather. 
           This is used in the SENSOR part of the Integration, so you can add as many data points as you like. 
           Then we can create a sensor for each of them in Home Assistant Later.
           Look in data/livedata.json for an example file
           DELETE this comment block, when you are done.
        """

        endpoint = f"{LIVE_BASE_URL}?key={self._api_key}&locatie={self._latitude},{self._longitude}"
        json_data = await self.async_request("get", endpoint)

        data = json_data["liveweer"]
        item = {}
        for row in data:
            item = {
                "location": row["plaats"],
                "station": row["station"],
                "temp": row["temp"],
                "feelslike": row["gtemp"],
                "dewpoint": row["dauwp"],
                "condition": row["samenv"],
                "icon": row["image"],
                "description": row["verw"],
                "humidity": row["lv"],
                "wind_direction": row["windr"],
                "wind_speed_ms": row["windms"],
                "wind_speed_bft": row["windbft"],
                "wind_speed_kmh": row["windkmh"],
                "wind_speed_knt": row["windknp"],
                "pressure_hpa": row["luchtd"],
                "visibility": row["zicht"],
                "day_temp_max": row["d0tmax"],
                "day_temp_min": row["d0tmin"],
                "day_icon": row["d0weer"],
                "day_precip_probability": row["d0neerslag"],
                "day_wind_speed_bft": row["d0windk"],
                "day_wind_speed_ms": row["d0windms"],
                "day_wind_direction": row["d0windr"],
                
            }

        return item

    async def hourly_data(self) -> None:
        """Returns json array with hourly forecast data."""

        """ERIK: The below functions return data for Hourly Forecast. 
           This is used in the WEATHER part of the Integration, so this need to have a fixed 
           set of data delivered to work with the Weather Integration.
           Look in data/hourly.json for an example file
           DELETE this comment block, when you are done.
        """

        endpoint = f"{FORECAST_BASE_URL}?locatie={self._latitude},{self._longitude}&key={self._api_key}"
        json_data = await self.async_request("get", endpoint)

        """If API Key is invalid it does not return an error, but a json string, that
           contains the error. So we need to catch it here.
        """
        if "api_key_invalid" in json_data:
            raise InvalidApiKey("Your API Key is invalid or does not support this operation")

        items = []
        data = json_data["data"]
        for row in data[:24]: # Only use the next 24 hours
            item = {
                "timestamp": row["tijd"],
                "local_time": dt.strptime(row["tijd_nl"], "%d-%m-%Y %H:%M").isoformat(),
                "temp": row["temp"],
                "ico": row["ico"],
                "icoon": row["icoon"],
                "condition": row["samenv"],
                "wind_speed_ms": row["winds"],
                "precipitation": row["neersl"],
                "wind_bearing": row["windr"],
                "wind_direction": row["windrltr"],
            }
            items.append(item)

        return items


    async def daily_data(self) -> None:
        """Returns json array with daily forecast data."""

        """ERIK: The below functions return data for Daily Forecast. 
           This is used in the WEATHER part of the Integration, so this need to have a fixed 
           set of data delivered to work with the Weather Integration.
           As KNMI does not deliver day based data for free, we need to make our
           own dataset. So I loop through all data to get min/max and accumulated rain.
           Look in data/hourly.json for an example file
           DELETE this comment block, when you are done.
        """

        endpoint = f"{FORECAST_BASE_URL}?locatie={self._latitude},{self._longitude}&key={self._api_key}"
        json_data = await self.async_request("get", endpoint)

        """If API Key is invalid it does not return an error, but a json string, that
           contains the error. So we need to catch it here.
        """
        if "api_key_invalid" in json_data:
            raise InvalidApiKey("Your API Key is invalid or does not support this operation")

        items = []
        data = json_data["data"]
        """We need to save data in the loop, so create empty
           variables to hold the data.
        """
        local_time = None
        temp_max = -100
        temp_min = 100
        precipitation = 0
        condition = None
        icon = None
        wind_speed = 0
        wind_bearing = 0
        cnt = 0
        for row in data:
            # Do calculations while we are at the same day
            if row["tijd_nl"][:10] == local_time:
                # Max Temperature of the Day
                if int(row["temp"]) > int(temp_max):
                    temp_max = row["temp"]
                # Min Temperature of the day
                if int(row["temp"]) < int(temp_min):
                    temp_min = row["temp"]
                # We select the Weather Condition and icon at 12 noon
                if row["tijd_nl"][11:13] == "12":
                    condition = row["samenv"]
                    icon = row["icoon"]
                # Accumulate precipitation for the day
                precipitation = precipitation + abs(float(row["neersl"]))
                # Average Wind Speed and Bearing for the Day
                wind_speed = wind_speed + int(row["winds"]) # I use m/s, but there are other values available
                wind_bearing = wind_bearing + int(row["windr"])
                cnt = cnt + 1
                
            else:
                # Save data as we are changing to a new day
                if local_time is not None:
                    item = {
                        "local_time": dt.strptime(local_time, "%d-%m-%Y").isoformat(),
                        "temp_max": temp_max,
                        "temp_min": temp_min,
                        "precipitation": round(precipitation, 2),
                        "condition": condition,
                        "icon": icon,
                        "wind_speed": int(wind_speed / cnt),
                        "wind_bearing": int(wind_bearing / cnt),
                    }
                    items.append(item)

                    # Reset Values
                    local_time = None
                    temp_max = -100
                    temp_min = 100
                    precipitation = 0
                    condition = None
                    icon = None
                    wind_speed = 0
                    wind_bearing = 0
                    cnt = 0

                # Store the current day we are looping
                local_time = row["tijd_nl"][:10]
                # This will be used when we are past 12 noon current day
                condition = row["samenv"]
                icon = row["icoon"]

        return items


    async def raw_forecast_data(self) -> None:
        """Returns json array with raw forecast data."""

        """ERIK: The below functions return raw data from the API Call. 
           I just use this to save a new json data set, to check what
           data is available

           DELETE this comment block, when you are done.
        """

        endpoint = f"{FORECAST_BASE_URL}?locatie={self._latitude},{self._longitude}&key={self._api_key}"
        json_data = await self.async_request("get", endpoint)
        return json_data

    async def async_request(self, method: str, endpoint: str) -> dict:
        """Make a request against the KNMI API.
        
           ERIK: THis function handles the actual Web Requests to the
           API. And if successfull, return the json data. If not successfull
           it will raise an error, that we can check for in HA.
        """

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(
                method, endpoint
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data
        except asyncio.TimeoutError:
            raise RequestError(f"Request to endpoint timed out: {endpoint}")
        except ClientError as err:
            if "Forbidden" in str(err):
                raise InvalidApiKey("Your API Key is invalid or does not support this operation")
            else:
                raise RequestError(f"Error requesting data from {endpoint}: {str(err)}")
        except:
            raise RequestError(f"Error occurred: {sys.exc_info()[1]}")
        finally:
            if not use_running_session:
                await session.close()

