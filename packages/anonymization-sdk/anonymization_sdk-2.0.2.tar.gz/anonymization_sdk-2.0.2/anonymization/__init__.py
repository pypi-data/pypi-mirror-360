from . import *
import coloredlogs #type: ignore
# default colored logs level.
# You may override it by doing the same thing with 'DEBUG' after importing anonymization once
coloredlogs.install('INFO') #type: ignore
__version__ = '2.0.2'