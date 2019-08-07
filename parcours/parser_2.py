'''Module for parsing fit activity messages to model classes
'''

from pyproj import Proj, transform
from fitparse import FitFile
from collections import namedtuple

from models import Lap, Record, Activity


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


class Translation(namedtuple('Translation',['source_field','dest_attr','transformation'])):
    """Represents a single translation from a field on a fit message to
    an attribute on destination model object. An optional transformation 
    can be supplied as a function definition. This will be applied at 
    translation time.
    """
    __slots__ = ()

    def __new__(cls, source_field,dest_attr,transformation=None):
        return super(Translation, cls).__new__(cls,source_field,dest_attr,transformation)


class LapTranslation:
    source_msg_name = 'lap'
    dest_model = Lap

    translations = (
        Translation('start_time','start_dtm'),
        Translation('timestamp','end_dtm')
    )


class Translator:
    """Responsible for translating a fit message to a model object
    accoding to the provided translation.
    """

    def translate(self, message, translation):
        model = translation.dest_model()

        for tr in translation.translations:
            field_value = getattr(message, tr.source_field)
            
            if tr.transformation:
                setattr(model, tr.dest_attr, tr.transformation(field_value))
            else:
                setattr(model, tr.dest_attr, field_value)
            
        return model


def activity():
    activity = Activity()
    activity.laps = []
    activity.records = []

    return activity


def extract_data(file_path):
    ff = FitFile(file_path)

    data = []


def activity_from_file(file_path):
    activitee = activity()

    data = extract_data(file_path)
    # Create new activity via activity()
    # extract models from file
    # filter the appropriate models from the extracted data and set each collection on the activity
    # return the activity
    pass


if __name__ == "__main__":
    from fitparse import FitFile

    message_translators = {
        "lap":LapTranslation
    }

    file_name = '../diy-trainingpeaks/activities/2018-12-11-06-44-01.fit'

    ff = FitFile(file_name)

    translator = Translator()

    extracted_data = []

    for msg_name,msg_tn in message_translators.items():
        messages = ff.get_messages(msg_name)
        message_translation = msg_tn()

        for message in messages:
            msg_dto = MessageDTO(message)
            model = translator.translate(msg_dto,message_translation)
            extracted_data.append(model)

    print(extracted_data[0])