'''Module for parsing fit activity messages to model classes
'''

from .models import Lap


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