"""Fitviz sqlalchemy models

Classes defined in this module are used to populate the fitviz database
through the sqlalchemy ORM.

These classes correspond to fit message types of the Activity Fit File
type outlined in the fit sdk.

"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Activity(Base):
    """Represents an activity such as a ride. Provides a container for sensor
    and ride data. Loosely corresponds to the activity message of the Activity
    File fit file type.
    standard.
    """

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)

    started_dtm = Column(DateTime)
    file_name = Column(String(20))

    records = relationship("Record")
    laps = relationship("Lap")


class Record(Base):
    """Represents data sampled from the device during activity. Includes
    sensor data such as speed, heart rate, power, etc. Corresponds to the
    record message of the Activity File fit file type.
    """

    __tablename__ = "record"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"))

    record_dtm = Column(DateTime)
    heart_rate = Column(Integer)
    power = Column(Integer)
    cadence = Column(Integer, nullable=True)
    speed = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)
    altitude = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    latitude_mercator = Column(Float, nullable=True)
    longitude_mercator = Column(Float, nullable=True)

    def __repr__(self):
        return "<Record({!r})>".format(vars(self))


class Lap(Base):
    """Represents a lap i.e. where the device user has pressed the 'lap'
    button to signal the start/finish of a lap. Corresponds to the lap message
    of the Activity File fit file type.
    """
    __tablename__ = "lap"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)

    start_dtm = Column(DateTime, nullable=False)
    end_dtm = Column(DateTime, nullable=False)
