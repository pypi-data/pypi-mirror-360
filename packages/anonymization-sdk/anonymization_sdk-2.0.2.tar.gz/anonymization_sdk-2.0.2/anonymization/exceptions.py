import os
import anonymization
import functools
from logging import getLogger, FileHandler, Formatter
import tempfile
logger = getLogger(__name__)

# Create an error logger specifically for logging unexpected errors to /tmp/anonymization-sdk-errors.logs
error_logger = getLogger('Error')
error_logger.propagate = False

log_dir = os.path.expanduser("~/.anonymization-sdk")
os.makedirs(log_dir, exist_ok=True)  # Ensure the directory exists

log_file = os.path.join(log_dir, 'anonymization-sdk-errors.logs') 
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write(f"anonymization-sdk version: {anonymization.__version__}\n")
    os.chmod(log_file, 0o777)
error_file_handler=FileHandler(log_file)
error_file_handler.setFormatter(Formatter('%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'))
error_logger.addHandler(error_file_handler)

# Root Exception Class for all Anonymization related Exceptions
class AnonymizationException(Exception):...


class InvalidCredentials(AnonymizationException):...


# Error representing invalid Id for any or detectionId,VideoId,GraphId,NodeId,EdgeId,etc
class InvalidIdError(AnonymizationException):...


# If an api returns response_code > 200
class InvalidAPIResponse(AnonymizationException):...

# VideoUrl doesn't exist anymore
class DownloadFailed(AnonymizationException):...

# Raise when you need to raise value error but handle gracefully since it's client facing
class AnonymizationValueError(AnonymizationException):...


def handle_anonymization_exceptions(default_factory):
    """Run the func and catch AnonymizationExceptions, and return a default output
    Decorate functions that run in multiprocessing, to process videos/galleries/etc
    in parallel, so that they can be gracefully handled to return some default value
    """
    def caller(func):
        @functools.wraps(func)
        def inner(*args,**kwargs):
            try:
                return func(*args, **kwargs)
            except AnonymizationException as e:
                logger.error(e)
                logger.debug(e, exc_info=True)
                return default_factory()
            except Exception as e:
                logger.error(f"Unexpected error occured: {e}. Please report with the log file {log_file}")
                error_logger.error(f"{'-'*80}\n{'-'*80}\n{e}\n\nargs:{args}\n\nkwargs: {kwargs}", exc_info=True)
                return default_factory()
        return inner
    return caller