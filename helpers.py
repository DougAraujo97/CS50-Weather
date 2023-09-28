import requests

from flask import redirect, session
from functools import wraps
from geopy.geocoders import Nominatim


# Borrowed login_required() from CS50 Finance
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Open-Meteo API only works with Latitude & longitude, so Nominatim gets that for us
def getLatLong(city):
    try:
        # initialize nominatim API
        geolocator = Nominatim(user_agent="MyApp")

        location = geolocator.geocode(city)

        # get lat and long attributes from the location object
        lat = location.latitude
        long = location.longitude

        return lat, long

    except AttributeError:
        raise AttributeError


def lookup(city):
    lat, long = getLatLong(city)

    # prepare Open-Meteo API
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={long}"
        f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
        f"&current_weather=true&timezone=auto&forecast_days=14"
    )

    # query Open_Meteo API
    response = requests.get(url).json()

    # current weather data
    temp = int(response["current_weather"]["temperature"])
    maxtemp = int(response["daily"]["temperature_2m_max"][0])
    mintemp = int(response["daily"]["temperature_2m_min"][0])
    sunrise = response["daily"]["sunrise"][0]
    sunset = response["daily"]["sunset"][0]
    precipitation_chance = response["daily"]["precipitation_probability_max"][0]
    windspeed = int(response["current_weather"]["windspeed"])
    is_day = response["current_weather"]["is_day"]

    # 14-day forecast data
    maxtemps = [int(i) for i in response["daily"]["temperature_2m_max"]]
    mintemps = [int(i) for i in response["daily"]["temperature_2m_min"]]
    sunrises = [i for i in response["daily"]["sunrise"]]
    sunsets = [i for i in response["daily"]["sunset"]]
    precipitation_chances = [
        i for i in response["daily"]["precipitation_probability_max"]
    ]

    # reverse lists so we get the data from least to most current
    maxtemps.reverse()
    mintemps.reverse()
    sunrises.reverse()
    sunsets.reverse()
    precipitation_chances.reverse()

    # Delete the first 4 items in each list since we're presenting a 10-day forecast, not a 14-day forecast
    del maxtemps[0:4]
    del mintemps[0:4]
    del sunrises[0:4]
    del sunsets[0:4]
    del precipitation_chances[0:4]

    # return data to app.py
    return {
        "temp": temp,
        "maxtemp": maxtemp,
        "mintemp": mintemp,
        "sunrise": sunrise,
        "sunset": sunset,
        "precipitation_chance": precipitation_chance,
        "windspeed": windspeed,
        "is_day": is_day,
        "maxtemps": maxtemps,
        "mintemps": mintemps,
        "sunrises": sunrises,
        "sunsets": sunsets,
        "precipitation_chances": precipitation_chances,
    }
