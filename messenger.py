import requests
import pandas as pd
import subprocess
from datetime import datetime
import schedule
import time


WEATHER_DATA_FILE = "hourly_weather_data.csv"
UPDATE_DF_PATH="api_call.py"
THRESHOLD_AMOUNT = 40 # in percentage
HIGH_RAINFALL = 70


columns_to_read = ["date", "precipitation_probability"]
read_hourly_dataframe = pd.read_csv(WEATHER_DATA_FILE, usecols=columns_to_read)

def update_dataframe(script_path):
    try:
        subprocess.run(['python',script_path],check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    return True


def filter_dates_by_amount(dataframe,lower_limit,upper_limit):
    filtered_dates = dataframe[(dataframe['precipitation_probability'] > lower_limit) & (dataframe['precipitation_probability'] < upper_limit)]['date'].tolist()
    return filtered_dates


def send_message(phone_number, message):
    resp = requests.post('https://textbelt.com/text', {
      'phone': f'{phone_number}',
      'message': f'{message}',
      'key': 'textbelt',
    })
    return resp.json()


def main():
    update_dataframe(UPDATE_DF_PATH)

    current_datetime_str= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.strptime(current_datetime_str, "%Y-%m-%d %H:%M:%S")
    print("Current date and time:", current_datetime)
    # print(read_hourly_dataframe[:24])

    moderate_rainy_hours = [hr[11:16] for hr in filter_dates_by_amount(read_hourly_dataframe[:24], THRESHOLD_AMOUNT,HIGH_RAINFALL)]
    high_rainy_hours = [hr[11:16] for hr in filter_dates_by_amount(read_hourly_dataframe[:24], HIGH_RAINFALL, 100)]

    print(moderate_rainy_hours)
    print(high_rainy_hours)

    if moderate_rainy_hours or high_rainy_hours:
        message = f"Moderate chance of rainfall is expected at  hours {moderate_rainy_hours}\n\nHigh chance of rainfall is expected at {high_rainy_hours}"

    else:
        message = "No rain expected today"

    print(send_message("+254115361123",message))

schedule.every().day.at("00:00").do(main())

while True:
    schedule.run_pending()
    time.sleep(600)