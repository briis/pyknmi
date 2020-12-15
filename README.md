# pyknmi
Python Wrapper for the dutch KNMI Weather API
A Python Wrapper to communicate with dutch KNMI Weather API from [METEOSERVER](https://meteoserver.nl)

This wrapper requires an API Key which you can get free from Meteoserver. Please respect the daily limit of 500 requests on the Free version.

### Testing
To run `test_client.py` first create a file called `settings.json` in the same directory, and put the following contents in there:

````
{
    "connection": {
        "api_key": "YOUR_API_KEY"
    }
}
````