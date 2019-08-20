"""
parcours.database
~~~~~~~~~~~~~~~

This module contains functionality for setting up and loading the
parcours database.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import config
from .models import Base


def load_db():
    """
    Sets up and populates the parcours database. Will create db and
    schema if does not exist. Reads activity files from the activity
    directory and loads them to the db.
    """

    engine = create_engine("sqlite:///{}".format(config["db_uri"]), echo=True)
    Base.metadata.create_all(engine)
