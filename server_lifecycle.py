"""
server_lifecycle
~~~~~~~~~~~~~~~

Bokeh Server Lifecycle Hooks. Code here is designed to be exectuted at
certain times in the server session or lifetime.
"""


def on_server_loaded(server_context):
    """Function called when bokeh server first starts."""
    print("Server started. on_server_loaded called. Preparing database.")
