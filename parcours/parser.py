'''Module for parsing fit activity messages to model classes
'''

from pyproj import Proj, transform

from .models import Lap, Record


DEGREES_MULTIPLIER = 180 / 2 ** 31


class MessageWrapper:
    '''A wrapper around a fit message make it easier to work with.
    
    Provides access into the field data through attribute access. When
    an attribute is accessed the wrapper will look inside the message's 
    field data and return its value if it exists and an AttributeError
    if it not.
    '''

    def __init__(self, message):
        self.message = message
        self.message_name = message.name

    def __getattr__(self, attr):
        field_data = next(filter(lambda f: f.name==attr,self.message.fields), None)
        
        if not field_data:
            raise AttributeError("'{}' message has no field named '{}'".format(self.message.name, attr))
        
        return field_data.value


class LapMapper:

    def __init__(self, source_msg):
        self.source_msg = source_msg
        self.dest_model = Lap()

        self.apply_mapping()

    def apply_mapping(self):
        mapping = {
            'start_dtm': self.source_msg.start_time,
            'end_dtm': self.source_msg.timestamp
        }

        self.dest_model.__dict__.update(mapping)

    def mapped_model(self):
        return self.dest_model


class RecordMapper:

    def __init__(self, source_msg):
        self.source_msg = source_msg
        self.dest_model = Record()

        self.apply_mapping()

    def apply_mapping(self):
        mapping = {
            "recorded_dtm": self.source_msg.timestamp,
            "heart_rate":self.source_msg.heart_rate,
            "power": self.source_msg.power,
            "cadence": self.source_msg.cadence,
            "speed": self.source_msg.speed,
            "distance": self.source_msg.distance,
            "altitude": self.source_msg.altitude,
            "latitude": self.semicircles_to_degrees(self.source_msg.position_lat),
            "longitude": self.semicircles_to_degrees(self.source_msg.position_long)
        }

        mapping["longitude_mercator"], mapping["latitude_mercator"] = self.latlong_to_mercator(mapping["longitude"],mapping["latitude"])

        self.dest_model.__dict__.update(mapping)

    def semicircles_to_degrees(self,semicircle):
        degrees = semicircle * (DEGREES_MULTIPLIER)
        return round(degrees,6)

    def latlong_to_mercator(self,long,lat):
        latlong = Proj(init='epsg:4326')
        mercator = Proj(init='epsg:3857')

        return transform(latlong,mercator,long,lat)

    def mapped_model(self):
        return self.dest_model