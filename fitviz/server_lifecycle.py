"""Server Lifecycle Hooks module.

Bokeh Server Lifecycle Hooks. Code here is designed to be exectuted at
certain times in the server session or lifetime.

"""
from fitviz import database


def on_server_loaded(server_context):
    """Function called when bokeh server first starts."""
    database.load_db()
