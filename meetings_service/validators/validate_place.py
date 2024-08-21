import os

import geopy.distance
import requests


def validate_place(place: str):
    api_key = os.getenv("YANDEX_MAPS_API_KEY")
    response = requests.get(
        f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={place}&format=json"
    ).json()
    try:
        point = response["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"
        ]["Point"]["pos"]
    except (KeyError, IndexError):
        return False
    lon, lat = map(float, point.split())
    center_lat, center_lon = 55.755811, 37.617617  # Moscow center
    return geopy.distance.distance((lat, lon), (center_lat, center_lon)).km < 10
