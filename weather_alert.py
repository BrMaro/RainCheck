import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from win10toast import ToastNotifier
from datetime import datetime

# Initialize toast notifier
toaster = ToastNotifier()

def fetch_weather_data():
    """Fetch weather data from Open-Meteo API"""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -1.2833,
        "longitude": 36.8167,
        "hourly": ["precipitation_probability", "precipitation", "rain"],
        "timezone": "Africa/Nairobi",
        "forecast_days": 1
    }
    
    response = openmeteo.weather_api(url, params=params)[0]
    
    # Process hourly data
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "precipitation_probability": hourly.Variables(0).ValuesAsNumpy(),
        "precipitation": hourly.Variables(1).ValuesAsNumpy(),
        "rain": hourly.Variables(2).ValuesAsNumpy()
    }
    
    return pd.DataFrame(data=hourly_data)

def get_rain_forecast(dataframe, threshold_moderate=40, threshold_high=70):
    """Analyze weather data and return rain forecast messages"""
    def filter_dates_by_amount(df, lower_limit, upper_limit):
        filtered = df[
            (df['precipitation_probability'] > lower_limit) & 
            (df['precipitation_probability'] < upper_limit)
        ]
        return [(time.strftime('%H:%M'), prob) for time, prob in 
                zip(filtered['date'], filtered['precipitation_probability'])]

    moderate_rain_times = filter_dates_by_amount(dataframe, threshold_moderate, threshold_high)
    heavy_rain_times = filter_dates_by_amount(dataframe, threshold_high, 100)

    messages = []
    if heavy_rain_times:
        times_str = ", ".join([f"{time} ({prob:.0f}%)" for time, prob in heavy_rain_times])
        messages.append(f"High chance of rain at: {times_str}")
    if moderate_rain_times:
        times_str = ", ".join([f"{time} ({prob:.0f}%)" for time, prob in moderate_rain_times])
        messages.append(f"Moderate chance of rain at: {times_str}")
    
    if not messages:
        return "No significant rain expected today"
    
    # Find earliest rain time with highest probability
    all_rain_times = moderate_rain_times + heavy_rain_times
    if all_rain_times:
        earliest_time, prob = min(all_rain_times, key=lambda x: x[0])
        messages.append(f"\nEarliest expected rain: {earliest_time} ({prob:.0f}% chance)")
    
    return "\n".join(messages)

def main():
    """Main function to check weather and show notification"""
    try:
        print(f"Fetching forecast at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch weather data
        weather_df = fetch_weather_data()
        
        # Get forecast message
        forecast_message = get_rain_forecast(weather_df)
        
        # Show Windows notification
        toaster.show_toast(
            "Daily Rain Forecast",
            forecast_message,
            duration=10,
            icon_path=None,
            threaded=True
        )
        
        print(forecast_message)
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main() 