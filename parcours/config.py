import configparser
import os

CONFIG_PATH = os.getenv('PARCOURS_CONF')


def _initialise():
    cp = configparser.SafeConfigParser()
    cp.read(CONFIG_PATH)
    
    return cp

# Could this be used instead to simplify config?
# http://www.voidspace.org.uk/python/articles/configobj.shtml#the-advantages-of-configobj

config = _initialise()

if __name__ == "__main__":
    print(config["application"]["binders"])