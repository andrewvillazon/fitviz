"""Fitviz configuration module

This module provides configuration values for fitviz. Default values can be 
overridden by modifying config.ini in the resources/configuration directory.

"""

import os
from configobj import ConfigObj


RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
CONFIG_PATH = os.path.join(RESOURCES_PATH, "configuration", "config.ini")
DEFAULT_DB_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "resources",
    "database",
    "activity.db",
)
DEFAULT_ACTIVITIES_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "resources",
    "activities",
)


config = ConfigObj(CONFIG_PATH)


if not config["db_uri"]:
    config["db_uri"] = DEFAULT_DB_PATH

if not config["activity_dir"]:
    config["activity_dir"] = DEFAULT_ACTIVITIES_PATH
