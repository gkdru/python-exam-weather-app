import requests


def get_weather(city):
    resp = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=c4f7874f9fc064b9bb8b2a60dc0d3f57&units=metric"
    ).json()
    data = resp
    return data
