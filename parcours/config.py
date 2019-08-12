import configparser
import os

CONFIG_DIR = os.getenv('PARCOURS_CONF')

class Configuration:
    def __init__(self, config_parser):
        parser = config_parser
    
    def __getattr__(self,attr):
        return self.parser.get(attr, None)


cp = configparser.SafeConfigParser()
cp.read(CONFIG_DIR)
config = Configuration(config_parser)

# TODO: Add nested attribute access to support config.section.value
# TODO: http://code.activestate.com/recipes/577346-getattr-with-arbitrary-depth/
# TODO: http://code.activestate.com/recipes/426406-an-easy-to-use-configuration-reader/
