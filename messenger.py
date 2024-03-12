import requests
import pandas as pd


WEATHER_DATA_FILE = "hourly_weather_data.csv"
THRESHOLD_AMOUNT = 0.4

columns_to_read = ["date", "rain"]
read_hourly_dataframe = pd.read_csv(WEATHER_DATA_FILE, usecols=columns_to_read)

def filter_dates_by_amount(dataframe,amount):
    filtered_dates = dataframe[dataframe['rain'] > amount]['date'].tolist()
    return filtered_dates

def send_message(phone_number, message):
    resp = requests.post('https://textbelt.com/text', {
      'phone': f'{phone_number}',
      'message': f'{message}',
      'key': 'textbelt',
    })
    return resp.json()

# print(send_message("+254115361123","Testing textbelt"))
