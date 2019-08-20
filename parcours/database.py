"""
parcours.database
~~~~~~~~~~~~~~~

This module contains functionality for setting up and loading the
parcours database.
"""

import os
import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import config
from .fileparser import activity_from_file
from .models import Base, Activity


engine = create_engine("sqlite:///{}".format(config["db_uri"]), echo=True)
Session = sessionmaker(bind=engine)


def activities_in_dir():
    """
    Returns a list of the activity files in the activity directory.
    """
    file_names = []

    for file_name in os.listdir(config["activity_dir"]):
        if file_name.endswith(".fit"):
            file_names.append(file_name)

    return file_names


def saved_activities():
    """
    Returns a list of the activity files currently stored in the
    parcours database.
    """
    file_names = []
    session = Session()

    for activity in session.query(Activity.file_name).all():
        file_names.append(activity.file_name)

    return file_names


def unsaved_activities():
    """Determines the activities in the activity dir not yet saved."""
    return list(set(activities_in_dir()) - set(saved_activities()))


def load_activity_files():
    """
    Loads to the parcours db any unsaved activities found in the activities
    directory.
    """
    unsaved_files = unsaved_activities()

    if not unsaved_files:
        return

    session = Session()

    for f in unsaved_files:
        activity = activity_from_file(os.path.join(config["activity_dir"], f))
        activity.file_name = f

        session.add(activity)
        session.commit()


def load_db():
    """
    Sets up and populates the parcours database. Will create db and
    schema if does not exist. Reads activity files from the activity
    directory and loads them to the db.
    """

    Base.metadata.create_all(engine)
    load_activity_files()
