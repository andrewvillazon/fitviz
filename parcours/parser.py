'''Module for parsing fit activity messages to model classes
'''

from . import models


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