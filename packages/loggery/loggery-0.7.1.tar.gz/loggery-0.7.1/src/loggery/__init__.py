"""loggery - Easy and standardized logging for Python

For command line tools, after creating your parser with `argparse`, pass it to `add_logging_args()`.
Then, after parsing arguments but before any logging, call
`configure_logging_from_args(args.verbose, args.quiet, args.log_stdout)`:

    import argparse
    import loggery

    parser = argparse.ArgumentParser()

    ... build your parser ...

    loggery.add_logging_args(parser)
    args = parser.parse_args()
    loggery.configure_logging_from_args(args.verbose, args.quiet, args.log_stdout)

This will set logging levels as requested by the command line options, with known external modules
that would otherwise flood the logs to be set slightly less verbose. The specific list is in
`loggery.SPAMMY_LOGGERS` and can be edited before calling any configure logging function.

The default log levels in `loggery.DEFAULT_LOG_LEVEL` and `loggery.DEFAULT_SPAMMY_LOG_LEVEL` can
also be modified, if desired. These do not support custom logging levels, however.

You may also pass a `logger_name` as a fourth argument to `configure_logging_from_args()` if you
don't want to use the root logger.

Finally, you can also call `configure_logging()` with specific log levels directly if needed.

Once configured, each module or scripts should generate log messages with the default logger for
their name:

    import logging
    LOG = logging.getLogger(__name__)

Then just write to the log using that logger:

    LOG.debug('This is a debug level log message.')
    LOG.info('This is an info level log message.')
    LOG.warning('This is a warning level log message.')
    LOG.error('This is an error level log message.')
    LOG.critical('This is a critical level log message.')
"""

import sys
import argparse
import importlib.metadata
import logging

__version__ = importlib.metadata.version("loggery")
__author__ = "erskin@eldritch.org"

# A set of loggers which we generally DON'T want to be quite as verbose as our main logger.
# By default, if we are being more verbose, these are set to one log level less verbose than the
# main log. If needed, you can add or remove items from this list before calling and configure
# logging function.
SPAMMY_LOGGERS = [
    "google.auth.transport.requests",
    "urllib3.util.retry",
    "boxsdk.auth.oauth2",
    "boxsdk.network.default_network",
    "urllib3.connectionpool",
    "gql.transport.requests",
    "requests",
]

DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_SPAMMY_LOG_LEVEL = logging.WARNING

_LOG_LEVELS = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
]

_LOG_FORMAT = "{asctime} [{levelname}] {name} - {message}"


def add_logging_args(parser: argparse.ArgumentParser):
    """Add --verbose, --quiet, --log-stdout arguments to the given argument parser."""

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=(
            "increase level of feedback output. Use -vv for even more detail. Log level defaults "
            "to " + repr(logging.getLevelName(DEFAULT_LOG_LEVEL))
        ),
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="decrease level of feedback output. Use -qq for even less detail",
    )
    parser.add_argument(
        "--log-stdout",
        action="store_true",
        help="direct all logging to standard out instead of standard error",
    )


def configure_logging_from_args(
    verbose: int = 0,
    quiet: int = 0,
    log_stdout: bool = False,
    remove_existing_handlers: bool = False,
    logger_name: str | None = None,
):
    """Configure logging based on the number of verbose and quiet flags and the log_stdout flag
    added by add_logging_args().

    Spammy loggers are those which, at more verbose log levels, are usually more noisy than useful.

    Known spammy loggers in `loggery.SPAMMY_LOGGERS` are set up to two levels less verbose than
    the main logger, but only when we are increasing the default verbosity.

    With the standard defaults, this means that as verbosity goes up, the main logger will go from
    WARNING to INFO, then DEBUG, and only then will the spammy loggers be set INFO, and then DEBUG.
    But, as verbosity goes down, both the main and spammy loggers will be set to ERROR, and then
    CRITICAL together.
    """

    # Set the log verbosity to the default, plus the count of verbose flags minus the count of
    # quiet flags.
    default_index = _LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    verbosity = default_index + verbose - quiet

    # Set the spammy loggers to track the verbosity of the main loggers to start.
    spammy_verbosity = verbosity
    if verbosity > default_index:
        # But if we are being more verbose than normal, keep the spammy loggers quieter than the
        # main ones, though never more quiet than the default spammy level.
        default_spammy_index = _LOG_LEVELS.index(DEFAULT_SPAMMY_LOG_LEVEL)
        spammy_verbosity = max(verbosity - 2, default_spammy_index)

    # Cap the verbosity and spammy verbosity to indexes of LOG_LEVELS.
    verbosity = min(verbosity, len(_LOG_LEVELS) - 1)
    verbosity = max(verbosity, 0)
    spammy_verbosity = min(spammy_verbosity, len(_LOG_LEVELS) - 1)
    spammy_verbosity = max(spammy_verbosity, 0)

    configure_logging(
        _LOG_LEVELS[verbosity],
        _LOG_LEVELS[spammy_verbosity],
        log_stdout,
        remove_existing_handlers,
        logger_name,
    )


def configure_logging(
    log_level: int | None = None,
    spammy_log_level: int | None = None,
    log_stdout: bool = False,
    remove_existing_handlers: bool = False,
    logger_name: str | None = None,
):
    """Setup the specified logger to the given level and the standard format, and the level of
    known spammy loggers.

    This will remove any existing log handlers.
    """

    if not log_level:
        log_level = DEFAULT_LOG_LEVEL

    if not spammy_log_level:
        spammy_log_level = DEFAULT_SPAMMY_LOG_LEVEL

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Remove any existing handlers if requested
    if remove_existing_handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    # Setup the message handler and formatter.
    stream = sys.stdout if log_stdout else sys.stderr
    handler = logging.StreamHandler(stream)
    handler.setLevel(log_level)
    formatter = logging.Formatter(_LOG_FORMAT, style="{")
    handler.setFormatter(formatter)

    # Add the handler to the logger.
    logger.addHandler(handler)

    # Set the known spammy loggers to the request log level.
    for spammy_logger_name in SPAMMY_LOGGERS:
        logging.getLogger(spammy_logger_name).setLevel(spammy_log_level)
