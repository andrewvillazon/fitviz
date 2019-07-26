'''Module for parsing fit activity messages to model classes
'''


class FitMsg:
    '''Container for a fit message. Attributes dynamically assigned.'''

    def __init__(self, msg_name):
        self.msg_name = msg_name