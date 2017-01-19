# GraylogHandler
A simple Python module which which is used with the `logging` module to send messages to a Graylog server. This handler attempts to send log messages to two different Graylog server by default. Those servers are:

| Address | TCP port | Description |
|:--------|:--------:|:------------|
|localhost|12201     |See link to vagrant machine below.|
|192.168.12.11| 12201| Server running on the DMSC network.|

A Vagrant file for setting up a virtual machine listening to localhost port 12201 can be found [here](https://bitbucket.org/europeanspallationsource/dm-graylog-machine). A sister project which implements a simple logging library (with Graylog comunication functionality) is [dm-graylog-logger](https://bitbucket.org/europeanspallationsource/dm-graylog-logger).

## Requirements
The module uses only standard Python packages. This module has been tested with Python 2.7 and Python 3.5 and should in principle work with every version in between. However, when using Python 2.7 the *future* package (containing Python 3.x functionality) must be installed (using e.g. pip):

```
pip2.7 install future
```

## Installation
Install the package by typing the following line in the GraylogHandler directory:

```
python setup.py install
```

Alternatively, copy the GraylogHandler directory to the location of your Python application.

## Usage
Only three lines are required for basic usage of this module:

```python
import logging
from GraylogHandler import GraylogHandler
logging.getLogger().addHandler(GraylogHandler())
```

All log messages produced using the builtin `logger` module will now also be sent to Graylog servers running on the local machine and listening on port 12201, e.g.:

```python
logging.error("This is a fatal error!")
```

## Documentation
Documentation with examples can be found on the ESS wiki: ???