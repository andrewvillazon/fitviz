from bokeh.models.widgets import Select
from bokeh.plotting import curdoc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from parcours.config import config
from parcours.models import Activity


# Connect to data
engine = create_engine(f"sqlite:///{config['db_uri']}", echo=False)
Session = sessionmaker(bind=engine)
session = Session()


# Setup widgets
activities = session.query(Activity.id, Activity.file_name).all()
activity_select = Select(title="Activity", options=activities)


# Define widget callback
def update(attr, old, new):
    print(attr, old, new)


# Register callback on widget
activity_select.on_change('value', update)


# Finally add to current document for rendering
curdoc().add_root(activity_select)
