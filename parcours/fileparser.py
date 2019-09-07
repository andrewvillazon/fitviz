"""Module providing functionality to parse a fit file into an
activity domain object.

Main interface is activity_from_file()
"""
import os

import pyproj
from fitparse import FitFile

from .models import Activity, Lap, Record


_DEGREES_MULTIPLIER = 180 / 2 ** 31


def _semicircles_to_degrees(lat_semi, long_semi):
    """Transforms a Lat Long pair in semicircles to decimal degrees."""
    return (
        round(lat_semi * (_DEGREES_MULTIPLIER), 6),
        round(long_semi * (_DEGREES_MULTIPLIER), 6),
    )


def _latlong_to_merc(lat, long):
    """Transforms a Lat Long pair to the Web Mercator projection."""
    latlong = pyproj.Proj(init="epsg:4326")
    mercator = pyproj.Proj(init="epsg:3857")

    return pyproj.transform(latlong, mercator, long, lat)


def _get_field_values(fit_msg):
    """Returns a dict of field names and values for the given fit message."""
    return {field.name: field.value for field in fit_msg.fields}


def _map_lap(lap_msg):
    """Maps a fit lap message type to a Lap model class"""
    msg_data = _get_field_values(lap_msg)
    return Lap(start_dtm=msg_data.get("start_time"), end_dtm=msg_data.get("timestamp"))


def _map_record(record_msg):
    """Maps a fit record message type to a Record model class"""
    msg_data = _get_field_values(record_msg)

    record = Record(
        record_dtm=msg_data.get("timestamp"),
        heart_rate=msg_data.get("heart_rate"),
        power=msg_data.get("power"),
        cadence=msg_data.get("cadence"),
        speed=msg_data.get("speed"),
        distance=msg_data.get("distance"),
        altitude=msg_data.get("altitude"),
    )

    latitude = msg_data.get("position_lat")
    longitude = msg_data.get("position_long")

    if latitude and longitude:
        record.latitude, record.longitude = _semicircles_to_degrees(latitude, longitude)
        record.latitude_mercator, record.longitude_mercator = _latlong_to_merc(
            record.latitude, record.longitude
        )

    return record


def _activity_start(fit_file):
    """Retrieves when the activity started from the given fit file"""
    session_msg = next(fit_file.get_messages("session"))
    session = _get_field_values(session_msg)

    return session["start_time"]


def activity_from_file(file_path):
    """Builds an Activity model from a given fit file."""
    fit_file = FitFile(file_path)

    activity = Activity()

    activity.started_dtm = _activity_start(fit_file)
    activity.file_name = os.path.basename(file_path)

    activity.laps = list(_map_lap(lap) for lap in fit_file.get_messages("lap"))
    activity.records = list(
        _map_record(record) for record in fit_file.get_messages("record")
    )

    return activity
