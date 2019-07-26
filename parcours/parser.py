'''Module for parsing fit activity messages to model classes
'''

from . import models


class FitMessageData:
    '''A wrapper around a fit message field data.
    
    Takes a fit message and sets the message's field data to the objects
    attributes. Makes the message easier to use by providing direct
    access to the field names and data.
    '''

    def __init__(self, message):
        self.message_name = message.name
        self.__dict__.update(self.extract_field_data(message.fields))

    def extract_field_data(self,fields):
        field_data = {}
        
        for field in fields:
            field_data[field.name]=field.value

        return field_data