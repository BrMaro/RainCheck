import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -1.3802,
	"longitude": 36.7463,
	"hourly": ["precipitation_probability", "precipitation", "rain"],
	"timezone": "auto"
}
responses = openmeteo.weather_api(url, params=params)