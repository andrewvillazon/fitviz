'''Module for parsing fit activity messages to model classes
'''

from pyproj import Proj, transform
from fitparse import FitFile

from .models import Lap, Record, Activity


DEGREES_MULTIPLIER = 180 / 2 ** 31
REQUIRED_MSG_TYPES = ['lap','record']


class MessageDTO:
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
        self.mapped_model = None
    
    def prepare_model(self):
        record = Record()
        
        record.recorded_dtm = self.source_msg.timestamp
        record.heart_rate = getattr(self.source_msg, 'heart_rate', None)
        record.power = getattr(self.source_msg, 'power', None)
        record.cadence = getattr(self.source_msg, 'cadence', None)
        record.speed = getattr(self.source_msg, 'speed', None)
        record.distance = getattr(self.source_msg, 'distance', None)
        record.altitude = getattr(self.source_msg, 'altitude', None)

        record.latitude = self.semicircles_to_degrees(self.source_msg.position_lat) if hasattr(self.source_msg,'position_lat') else None
        record.longitude = self.semicircles_to_degrees(self.source_msg.position_long) if hasattr(self.source_msg,'position_long') else None
        # SEE HERE:
        # http://pyproj4.github.io/pyproj/stable/optimize_transformations.html#optimize-transformations
        if record.latitude and record.longitude:
            record.longitude_mercator, record.latitude_mercator = self.latlong_to_mercator(record.longitude,record.latitude)
        else:
            record.longitude_mercator, record.latitude_mercator = None, None

        return record


    def semicircles_to_degrees(self,semicircle):
        degrees = semicircle * (DEGREES_MULTIPLIER)
        return round(degrees,6)

    def latlong_to_mercator(self,long,lat):
        latlong = Proj(init='epsg:4326')
        mercator = Proj(init='epsg:3857')

        return transform(latlong,mercator,long,lat)

    @property
    def model(self):
        self.mapped_model = self.prepare_model()
        return self.mapped_model


def activity():
    activity = Activity()
    activity.laps = []
    activity.records = []

    return activity


def activity_from_file(file_path):
    new_activity = activity()

    fit_file = FitFile(file_path)

    for msg_type in REQUIRED_MSG_TYPES:
        messages = list(fit_file.get_messages(msg_type))

        for message in messages:
            better_msg = MessageDTO(message)

            if better_msg.message_name == 'lap':
                lap = LapMapper(better_msg).mapped_model()
                new_activity.laps.append(lap)
            
            if better_msg.message_name == 'record':
                record_mapper = RecordMapper(better_msg)
                new_activity.records.append(record_mapper.model)

    return new_activity