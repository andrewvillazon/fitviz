"""Fitviz database module

This module contains functionality for setting up and loading the fitviz 
database. The database is populated by searching the activity directory
for .fit files, parsing their contents, and loading their data to the db.

"""

import os
import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import config
from .fileparser import activity_from_file
from .models import Base, Activity


engine = create_engine(f"sqlite:///{config['db_uri']}", echo=True)
Session = sessionmaker(bind=engine)


def fit_files_in_dir():
    """Returns a list of the .fit files in the activity directory."""

    file_names = []

    for file_name in os.listdir(config["activity_dir"]):
        if file_name.endswith(".fit"):
            file_names.append(file_name)

    return file_names


def saved_fit_files():
    """Returns a list of .fit files stored in the fitviz database."""
    file_names = []
    session = Session()

    for activity in session.query(Activity.file_name).all():
        file_names.append(activity.file_name)

    return file_names


def unsaved_fit_files():
    """Determines the activities in the activity dir not yet saved."""
    return list(set(fit_files_in_dir()) - set(saved_fit_files()))


def load_fit_files():
    """
    Loads to the fitviz db any unsaved activities found in the activity
    directory.
    """
    unsaved_files = unsaved_fit_files()

    if not unsaved_files:
        return

    session = Session()

    for f in unsaved_files:
        activity = activity_from_file(os.path.join(config["activity_dir"], f))
        session.add(activity)
        session.commit()


def load_db():
    """
    Sets up and populates the fitviz database. Will create db and schema if it
    does not exist. Looks for new .fit files in the activity directory and
    loads them to the db.
    """

    Base.metadata.create_all(engine)
    load_fit_files()
