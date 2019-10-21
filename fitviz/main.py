import os
import time

import numpy as np
import pandas as pd
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Div, Select
from bokeh.palettes import Set3
from bokeh.plotting import curdoc, figure
from parcours.config import config
from parcours.models import Activity, Record
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'templates')


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


with open(os.path.join(TEMPLATES_PATH, 'dash_title.html')) as in_file:
    dash_title = in_file.read()

title = Div(text=dash_title, sizing_mode="stretch_width")


# Setup empty chart sources
with open(os.path.join(TEMPLATES_PATH, 'ride_summary.html')) as in_file:
    ride_summary_template = in_file.read()

data_stream_src = ColumnDataSource(
    data={
        "cumulative_time": [],
        "power": [],
        "heart_rate": [],
        "altitude": [],
        "speed": [],
    }
)

power_dist_src = ColumnDataSource(
    data={"bottom": [], "time_in_bin": [], "l_edge": [], "r_edge": []}
)

hr_dist_src = ColumnDataSource(
    data={"bottom": [], "time_in_bin": [], "l_edge": [], "r_edge": []}
)

pdc_src = ColumnDataSource(data={"durations": [], "mmp": []})


# Setup empty charts and glyphs
ride_summary = Div(sizing_mode="stretch_width")

data_stream_fig = figure(title="Data Stream", plot_height=250, plot_width=800)
data_stream_fig.xaxis.formatter = NumeralTickFormatter(format="00:00:00")
data_stream_fig.line(
    x="cumulative_time",
    y="altitude",
    line_width=1,
    source=data_stream_src,
    line_color=Set3[9][8],
)
data_stream_fig.line(
    x="cumulative_time",
    y="power",
    line_width=1,
    source=data_stream_src,
    line_color=Set3[9][4],
)
data_stream_fig.line(
    x="cumulative_time",
    y="heart_rate",
    line_width=1,
    source=data_stream_src,
    line_color=Set3[9][3],
)

power_dist_fig = figure(title="Power Distribution", plot_height=250, plot_width=400)
power_dist_fig.quad(
    bottom="bottom",
    top="time_in_bin",
    left="left_edge",
    right="right_edge",
    source=power_dist_src,
    color=Set3[9][4],
)

hr_dist_fig = figure(title="Heart Rate Distribution", plot_height=250, plot_width=400)
hr_dist_fig.quad(
    bottom="bottom",
    top="time_in_bin",
    left="left_edge",
    right="right_edge",
    source=hr_dist_src,
    color=Set3[9][3],
)

pdc_fig = figure(title="Power Duration Curve", plot_height=250, plot_width=800, x_axis_type="log")
pdc_fig.circle(x="durations", y="mmp", source=pdc_src, color=Set3[9][4])


# Prepare chart data
def ride_summary_text(df):
    df = df.fillna(0)

    return ride_summary_template.format(
        distance=df["distance"].max(),
        duration=time.strftime('%H:%M:%S', time.gmtime(len(df.index))),
        avg_speed=(df["speed"].mean()) * 3.6,
        avg_hr=df["heart_rate"].mean(),
        avg_power=df["power"].mean()
    )

def actvitiy_df(activity_id):
    query = session.query(Record).filter(Record.activity_id == activity_id)
    df = pd.read_sql(query.statement, query.session.bind, index_col="record_dtm")

    return df


def data_stream_data(activity_df):
    # Adjust dataframe for this chart
    activity_df = activity_df.asfreq("S")
    activity_df["cumulative_time"] = range(1, len(activity_df) + 1)

    return {
        "record_dtm": activity_df.index.values,
        "cumulative_time": activity_df["cumulative_time"],
        "power": activity_df["power"],
        "heart_rate": activity_df["heart_rate"],
        "altitude": activity_df["altitude"],
        "speed": activity_df["altitude"],
    }


def round_up(x, up_to):
    return x if x % up_to == 0 else x + up_to - x % up_to


def distribution_data(activity_df, measure):
    series = activity_df[measure].fillna(0.0).astype(int)
    series = series[series > 0]

    if series.empty:
        return {"bottom": [], "time_in_bin": [], "left_edge": [], "right_edge": []}

    bin_size = 5
    top_of_bin_range = round_up(max(series), bin_size)

    hist, edges = np.histogram(
        series, bins=int(top_of_bin_range / bin_size), range=[0, top_of_bin_range]
    )

    return {
        "bottom": [0] * int(top_of_bin_range / bin_size),
        "time_in_bin": hist,
        "left_edge": edges[:-1],
        "right_edge": edges[1:],
    }


# Power duration curve
def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def max_mean_power(power, duration):
    if duration == 1:
        return max(power)

    return max(running_mean(power, duration))


def pdc_data(df):
    power = df['power'].dropna().values

    if power.size == 0:
        return {"durations": [], "mmp": []}

    durations = list(set(np.geomspace(start=1, stop=len(power), num=100, dtype=int).tolist()))
    mmp = [max_mean_power(power, duration) for duration in durations]

    return {"durations": durations, "mmp": mmp}


# Widget callback that will populate charts
def update(attr, old, new):
    df = actvitiy_df(int(new))
    data_stream_src.data = data_stream_data(df)
    power_dist_src.data = distribution_data(df, "power")
    hr_dist_src.data = distribution_data(df, "heart_rate")
    pdc_src.data = pdc_data(df)
    ride_summary.text = ride_summary_text(df)


# Register callback on widget
activity_select.on_change("value", update)


# Intital render of the charts on start
update(None, None, max(act[0] for act in activity_select_vals()))


# Layout
l = layout(
    [
        [title],
        [[activity_select, ride_summary], 
        [data_stream_fig, 
            [power_dist_fig, hr_dist_fig],
        pdc_fig
        ]
        ]
    ]
    )


# Add to current document for rendering
curdoc().add_root(l)
