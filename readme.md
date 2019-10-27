# FitViz

FitViz is a tool written in python for exploring and visualising .fit files. Currently only the activity file type is supported.

## Installation

To use FitViz clone (or download) the repo with the command below:

```bash
git clone https://github.com/andrewvillazon/fitviz.git
```
Install the required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

After you've cloned the repo copy your .fit files to the default activities directory:

```bash
fitviz/resources/activities/
```

With your .fit files in place the tool can be started. FitViz uses [bokeh](https://docs.bokeh.org/en/latest/index.html) server to serve its dashboard. To start enter the following command in your terminal:

```bash
bokeh serve fitviz
```

When started FitViz will parse any new fit files in the activity directory storing their data in its database. This may take a while first time. When this process is finished the files can be explored at: [http://localhost:5006/fitviz](http://localhost:5006/fitviz)

### Custom Activity Directory
If you would like to use a custom directory you can override the default by setting the `activity_dir` value of the `config.ini` file found in the `fitviz/resources/configuration/` directory.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Contributions could include:
* Unit tests
* New Visualisations
* Issue fixes
* New Dashboard functionality
* Support for other fit file types

### Additional information
FitViz makes use of the [fit standard by ANT](https://www.thisisant.com/developer/ant/ant-fs-and-fit1)

## License
[GNU GPL v3.0](https://choosealicense.com/licenses/gpl-3.0/)
