# *GraylogHandler* examples
Installation instructions can be found on the [GraylogHandler repository page](https://bitbucket.org/europeanspallationsource/grayloghandler/src). The intent of this wiki page is to give you examples on how GraylogHandler as well as the Python logger modules can be used. Full documentation on the Python `logging` module can be found here: [https://docs.python.org/2/library/logging.html](https://docs.python.org/2/library/logging.html).

## Simple Python logging example (without Graylog)
As simple as it gets:

```python
import logging
logging.warning("This is a warning message.")
```
This will print the following line to console:

```
WARNING:root:This is a warning message.
```

## Simple GraylogHandler example
Set-up the Python logging module to send Graylog messages to localhost and then send a message.

```python
import logging
from GraylogHandler import GraylogHandler
logging.getLogger().addHandler(GraylogHandler())
logging.error("This is a fatal error!")
```

This will send a log message to localhost 12201 but it will not print the message to console.

## Log to console, file and Graylog
```python
import logging
from GraylogHandler import GraylogHandler

#Almost the same as: logging.getLogger().addHandler(logging.FileHandler("messages.log"))
logging.basicConfig(filename="messages.log")

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().addHandler(GraylogHandler())
logging.warning("This is another warning.")
```

This will output the following line to the file `messages.log`.

```
WARNING:root:This is another warning.
```

And the following line to console:

```
This is another warning.
```

## Connect to another Graylog server
Connect to the Graylog server with hostname *somehost.com* listening on port *12201*. Note that it is possible to set GraylogHandler to send to several different hosts.

```python
import logging
from GraylogHandler import GraylogHandler
logging.getLogger().addHandler(GraylogHandler(servers = [["somehost.com", 12201], ]))
logging.error("This is a fatal error!")
```

## Change log message format
Note that it is not possible to set the Graylog message format this way.

```python
import logging
consoleHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
consoleHandler.setFormatter(formatter)
logging.getLogger().addHandler(consoleHandler)
logging.critical("This is critical!")
```

Outputs a line of the following shape to console:

```
2017-01-02 15:09:24,520 - CRITICAL - This is critical!
```

## Set global severity level
It is possible to set a limit to the severity level that is printed. By default only messages with a severity of warning and up are displayed.

```python
import logging
logging.debug("This will not be shown!")
logging.getLogger().setLevel(logging.DEBUG)
logging.debug("This will be shown.")
```

This code will output a single line to console:

```
DEBUG:root:This will be shown.
```

## Set severity level by handler
It is also possible to which minimum severity level will be used on each handler. Note that the global severity level must also be appropriately set for the handler to receive low severity events.

```python
import logging
from GraylogHandler import GraylogHandler

logging.getLogger().setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("messages.log")
fileHandler.setLevel(logging.CRITICAL)
logging.getLogger().addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.WARNING)
logging.getLogger().addHandler(consoleHandler)

grayHandler = GraylogHandler()
grayHandler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(grayHandler)

logging.critical("Shown everywhere.")
logging.warning("Shown on console and sent to Graylog server but not written to file.")
logging.debug("Only sent to Graylog server.")
```

Outputs the following line to file:

```
Shown everywhere.
```

This is written to the console:

```
Shown everywhere.
Shown on console and sent to Graylog server but not written to file.
```

And the Graylog server receives all three messages.