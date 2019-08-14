"""
parcours.config
~~~~~~~~~~~~~~~

This module contains the configuration values for parcours. Values are
read from a configuration file.
"""

import os
from configobj import ConfigObj


CONFIG_PATH = os.getenv("PARCOURS_CONF")

config = ConfigObj(CONFIG_PATH)
