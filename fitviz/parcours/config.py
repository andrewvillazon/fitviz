"""
parcours.config
~~~~~~~~~~~~~~~

This module contains the configuration values for parcours. Values are
read from a configuration file.
"""

import os
from configobj import ConfigObj


RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
CONFIG_PATH = os.path.join(RESOURCES_PATH, "configuration", "config.ini")

config = ConfigObj(CONFIG_PATH)
