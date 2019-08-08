"""Module providing functionality to parse a fit file into an
activity domain object.

Main interface is activity_from_file()
"""
import pyproj
from fitparse import FitFile

from .models import Lap, Record, Activity


DEGREES_MULTIPLIER = 180 / 2 ** 31


class MessageDTO:
    '''Wraps fit message to provide attribute access to message field data.
    '''

    def __init__(self, message):
        self.message = message

    def __getattr__(self, attr):
        field_data = next(filter(lambda f: f.name == attr,
                                 self.message.fields), None)

        if not field_data:
            raise AttributeError(
                "'{}' message has no field named '{}'".format(self.message.name, attr))

        return field_data.value


def _semicircle_to_degree(semicircle):
    degrees = semicircle * (DEGREES_MULTIPLIER)
    return round(degrees, 6)


def _semicircle_to_mercator(semicircle):
    # FIXME: Conversion to lat long requires x y pair
    return None


# TODO: Validate the mapping is consistent with model classes before use
mapping_config = {
    "message_to_model_mappings": [
        {
            "message_name": "lap",
            "model_class": Lap,
            "attribute_mappings": [
                {
                    "field": "start_time",
                    "attribute": "start_dtm"
                },
                {
                    "field": "timestamp",
                    "attribute": "end_dtm"
                }
            ]
        },
        {
            "message_name": "record",
            "model_class": Record,
            "attribute_mappings": [
                {
                    "field": "timestamp",
                    "attribute": "recorded_at"
                },
                {
                    "field": "heart_rate",
                    "attribute": "heart_rate"
                },
                {
                    "field": "power",
                    "attribute": "power"
                },
                {
                    "field": "cadence",
                    "attribute": "cadence"
                },
                {
                    "field": "speed",
                    "attribute": "speed"
                },
                {
                    "field": "distance",
                    "attribute": "distance"
                },
                {
                    "field": "altitude",
                    "attribute": "altitude"
                },
                {
                    "field": "position_lat",
                    "attribute": "latitude",
                    "transformation": _semicircle_to_degree
                },
                {
                    "field": "position_long",
                    "attribute": "longitude",
                    "transformation": _semicircle_to_degree
                },
                {
                    "field": "position_lat",
                    "attribute": "latitude_mercator",
                    "transformation": _semicircle_to_mercator
                },
                {
                    "field": "position_long",
                    "attribute": "longitude_mercator",
                    "transformation": _semicircle_to_mercator
                }
            ]
        }
    ]
}


def extract_data(fit_file):
    data = []

    for mapping in mapping_config["message_to_model_mappings"]:
        messages = list(fit_file.get_messages(mapping["message_name"]))

        for message in messages:
            message_dto = MessageDTO(message)
            model_class = mapping["model_class"]()

            for attribute_map in mapping["attribute_mappings"]:
                field_value = getattr(message_dto, attribute_map["field"], None)

                if "transformation" in attribute_map and field_value:
                    transformation_function = attribute_map["transformation"]
                    field_value = transformation_function(field_value)

                setattr(model_class, attribute_map["attribute"], field_value)

            data.append(model_class)

    return data


def activity(file_path, data):
    activity = Activity()
    activity.file_name = file_path
    activity.laps = list(filter(lambda x: isinstance(x, Lap), data))
    activity.records = list(filter(lambda x: isinstance(x, Record), data))

    return activity


def activity_from_file(file_path):
    fit_file = FitFile(file_path)
    data = extract_data(fit_file)

    return activity(file_path, data)