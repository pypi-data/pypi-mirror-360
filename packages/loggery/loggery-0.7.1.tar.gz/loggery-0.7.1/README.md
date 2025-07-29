loggery
=======
*Easy and standardized logging for Python*

Log Format
----------
This package configures logging with the following format:

    "{asctime} [{levelname}] {name} - {message}"

* asctime - Log message timestamp consisting of date and time (with ms) separated by a space
* levelname - Log level of the message
* name - Logger name
* message - Body of the log message

This produces log messages such as this:

    2022-04-29 10:38:52,315 [INFO] pyspam-app - Slicing 27 cans of spam into 6 slices each for a total of 162 slices.

Basic Usage
-----------
For command line tools, after creating your parser with `argparse`, pass it to `add_logging_args()`. Then, after parsing
arguments but before any logging, call `configure_logging_from_args(args.verbose, args.quiet, args.log_stdout)`:

    import argparse
    import loggery

    parser = argparse.ArgumentParser()

    ... build your parser ...

    loggery.add_logging_args(parser)
    args = parser.parse_args()
    loggery.configure_logging_from_args(args.verbose, args.quiet, args.log_stdout)

This will set logging levels as requested by the command line options, with known external modules that would otherwise
flood the logs to be set slightly less verbose. The specific list is in `loggery.SPAMMY_LOGGERS` and can be
edited before calling any configure logging function.

The default log levels in `loggery.DEFAULT_LOG_LEVEL` and `loggery.DEFAULT_SPAMMY_LOG_LEVEL` can also be modified, if
desired. These do not support custom logging levels, however.

You may also pass a `logger_name` as a fourth argument to `configure_logging_from_args()` if you don't want to use the root
logger. However, if your code is the main execution thread, you should generally configure the root logger so that all output
uses the same log format.

Finally, you can also call `configure_logging()` with specific log levels directly if needed.

Once configured, each module or scripts should generate log messages with the default logger for their name:

    import logging
    LOG = logging.getLogger(__name__)

Then just write to the log using that logger:

    LOG.debug('This is a debug level log message.')
    LOG.info('This is an info level log message.')
    LOG.warning('This is a warning level log message.')
    LOG.error('This is an error level log message.')
    LOG.critical('This is a critical level log message.')

Design Overview
---------------
The core assumptions are that logging should be easy to setup with reasonable defaults, configurable with command line options
at runtime, and allow fine control over the volume of information output.

To support this last point, there are modules that are commonly used and provide useful log information, but are also verbose
when set to more detailed log levels despite usually not being the log messages you are interested in. The requests module is a
great example of this. Debug level logs are verbose and produce tons of information, but the code itself is rarely the source
of issues. Setting a general log level of debug means seeing both the debug messages of the problematic code and modules like
requests, which just adds more messages to wade through that aren't helpful.

Because of this, loggery has a list of loggers which are known to be both reliable and noisy. When requesting more verbose
log information, these "spammy" loggers trail behind the general log level by two steps. This causes more relevant logs to be
displayed without the spammy logger information unless even more verbosity is requested.

In practice, with the default settings, it results in the following level of log output per verbose flag given:

| Verbosity | General Log Level | Spammy Logger Level |
|-----------|:-----------------:|:-------------------:|
| (none)    |      WARNING      |       WARNING       |
| `-v`      |       INFO        |       WARNING       |
| `-vv`     |       DEBUG       |       WARNING       |
| `-vvv`    |       DEBUG       |        INFO         |
| `-vvvv`   |       DEBUG       |        DEBUG        |

Configuration
-------------
The default log levels in `loggery.DEFAULT_LOG_LEVEL` and `loggery.DEFAULT_SPAMMY_LOG_LEVEL` are set to
WARNING and can be modified, if desired. Custom logging levels, however, are not supported.

The set of loggers considered spammy is an iterable in `loggery.SPAMMY_LOGGERS` and can also be modified or replaced.

Finally, while not recommended, the log format can be modified by changing the value in `loggery._LOG_FORMAT`. This
uses the curly brace style formatting. Note this specific attribute is internal may undergo breaking changes in the future.
The default format is: `"{asctime} [{levelname}] {name} - {message}"`

All configuration changes should be made before calling any configuration functions.

Function Overview
-----------------
For full details please see the source code and function documentation strings.

### `add_logging_args(parser: argparse.ArgumentParser)`

Adds the `--verbose`, `--quiet`, and `--log-stdout` options to the given argument parser. These arguments are used by
`configure_logging_from_args()`.

### `configure_logging_from_args(verbose: int = 0, quiet: int = 0, log_stdout: bool = False, logger_name: str = None)`

Configures the specified logger, typically the root logger, from the given number of verbose and quiet flags, and, when
increaing verbosity, sets the log level for known spammy loggers to trail behind by two log levels.

### `configure_logging(log_level: int = None, spammy_log_level: int = None, log_stdout: bool = False, logger_name: str = None)`

For the given logger, typically the root logger, overwrites the existing configuration to use the specified level and 
standard format. Also sets the spammy loggers to their specified level. This function is used by
`configure_logging_from_args()` and can alternately be called directly if needed.
