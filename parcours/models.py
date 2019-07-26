from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(20))

    records = relationship("Record", back_populates="record")
    laps = relationship("Lap", back_populates="lap")


class Record(Base):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"))

    recorded_dtm = Column(DateTime)
    heart_rate = Column(Integer)
    power = Column(Integer)
    cadence = Column(Integer,nullable=True)
    speed = Column(Integer,nullable=True)
    distance = Column(Float,nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class Lap(Base):
	__tablename__ = 'lap'

	id = Column(Integer, primary_key=True)
	activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)

	start_dtm = Column(DateTime, nullable=False)
	end_dtm = Column(DateTime, nullable=False)
