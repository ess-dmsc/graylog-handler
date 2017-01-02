# GraylogHandler
A simple Python module which which is used with the `logging` module to send messages to a Graylog server. This handler sends log messages to a Graylog server on localhost TCP port 12201 by default. A Vagrant file for setting up a virtual machine listening to this port can be found [here](https://bitbucket.org/europeanspallationsource/dm-graylog-machine). A sister project which implements a simple logging library (with Graylog comunication functionality) is [dm-graylog-logger](https://bitbucket.org/europeanspallationsource/dm-graylog-logger).

## Requirements
The module uses only standard Python packages. It has only been tested with Python version 3.5 but it should work with version 2.7 and up.

## Installation
Install the package by typing the following line in the GraylogHandler directory:

```
python setup.py install
```

Alternatively, copy the GraylogHandler directory to the location of your Python application.

## Usage
Only three lines are required for basic usage of this module:

```python
import logger
from GraylogHandler import GraylogHandler
logging.getLogger().addHandler(GraylogHandler())
```

All log messages produced using the builtin `logger` module will now also be sent to Graylog servers running on the local machine and listening on port 12201, e.g.:

```python
logger.error("This is a fatal error!")
```

## Documentation
Documentation with examples can be found on the ESS wiki: ???