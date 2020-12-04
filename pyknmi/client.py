"""Define a client to interact with KNMI."""
import asyncio
import sys
import logging
from typing import Optional

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

        endpoint = f"{LIVE_BASE_URL}?key={self._api_key}&locatie={self._latitude},{self._longitude}"
        json_data = await self.async_request("get", endpoint)

        item = {}
        for row in json_data["liveweer"]:
            item = {
                "location": row["plaats"],
                "temp": row["temp"],
                "feelslike": row["gtemp"],
                "dewpoint": row["dauwp"],
                "condition": row["samenv"],
                "icon": row["image"],
                "description": row["verw"],
                "humidity": row["lv"],
                "wind_direction": row["windr"],
                "wind_speed_ms": row["windms"],
                "wind_speed_bft": row["winds"],
                "wind_speed_kmh": row["windkmh"],
                "wind_speed_knt": row["windk"],
                "pressure_hpa": row["luchtd"],
                "visibility": row["zicht"],
                "day_temp_max": row["d0tmax"],
                "day_temp_min": row["d0tmin"],
                "day_icon": row["d0weer"],
                "day_precip_probability": row["d0neerslag"],
                "day_wind_speed_bft": row["d0windk"],
                "day_wind_direction": row["d0windr"],
                
            }

        return item

    async def async_request(self, method: str, endpoint: str) -> dict:
        """Make a request against the KNMI API."""

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

