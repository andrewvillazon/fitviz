import pandas as pd
from bokeh.layouts import Row
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Select
from bokeh.plotting import curdoc, figure
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from parcours.config import config
from parcours.models import Activity, Record


# Connect to data
engine = create_engine(f"sqlite:///{config['db_uri']}", echo=False)
Session = sessionmaker(bind=engine)
session = Session()


# Setup widgets
def activity_select_vals():
    activities = session.query(Activity.id, Activity.started_dtm).all()

    activities_formatted = []

    for activity in activities:
        activity_id = str(activity.id)
        start_dtm = activity[1].strftime("%d/%m/%Y - %I:%M %p")
        activities_formatted.append((activity_id, start_dtm))

    return activities_formatted

activity_select = Select(title="Activity", options=activity_select_vals())


# Setup empty chart sources
data_stream_src = ColumnDataSource(
    data={"cumulative_time": [], "power": [], "heart_rate": [], "altitude": [], "speed": []}
)


# Setup empty charts and glyphs
data_stream_fig = figure(title="Data Stream", plot_height=400, plot_width=800)
data_stream_fig.xaxis.formatter = NumeralTickFormatter(format='00:00:00')
data_stream_fig.line(x="cumulative_time", y="power", line_width=1, source=data_stream_src)


# Prepare chart data
def actvitiy_df(activity_id):
    query = session.query(Record).filter(Record.activity_id == activity_id)
    df = pd.read_sql(query.statement, query.session.bind, index_col="record_dtm")

    return df


def data_stream_data(activity_df):
    # Adjust dataframe for this chart
    activity_df = activity_df.asfreq("S")
    activity_df["cumulative_time"] = range(1, len(activity_df)+1)

    return {
        "record_dtm": activity_df.index.values,
        "cumulative_time": activity_df["cumulative_time"],
        "power": activity_df["power"],
        "heart_rate": activity_df["heart_rate"],
        "altitude": activity_df["altitude"],
        "speed": activity_df["altitude"],
    }


# Widget callback that will populate charts
def update(attr, old, new):
    df = actvitiy_df(int(new))
    data_stream_src.data = data_stream_data(df)


# Register callback on widget
activity_select.on_change("value", update)


# Intital render of the charts on start
update(None, None, max(act[0] for act in activity_select_vals()))


# Add to current document for rendering
curdoc().add_root(Row(activity_select, data_stream_fig))
