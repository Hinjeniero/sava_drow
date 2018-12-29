"""--------------------------------------------
logger module. Has all the classes, methods and attributes to
keep a log in real time, be it on screen or on a local file.
Have the following classes:
    Parser
    Logger
--------------------------------------------"""
__all__ = ['Parser', 'Logger']
__version__ = '0.8'
__author__ = 'David Flaity Pardo'

#Python libraries
import logging
import threading
import traceback
import time

"""Initialization of a basic logger. 
1.- It sets the level and above to which print the messages
2.- We establish the default logging out to be a file. In the format the hour is included.
3.- A new handler is created and configured in the same fashion. 
    This is needed to also show the log on screen (stdout), and not only in the file."""
LOGGING_LVL = logging.DEBUG
logging.basicConfig(filename='history.log', level=LOGGING_LVL, format='[%(asctime)s]: %(message)s \n')
std_handler = logging.StreamHandler()
std_handler.level       = LOGGING_LVL
std_handler.formatter   = logging.Formatter('[%(asctime)s] - %(message)s', "%H:%M:%S")
logging.getLogger().addHandler(std_handler)
LOG = logging.getLogger()

class Parser:
    """Parser class. Contains the static methods that in some way or anohter parse and convert content."""
    @staticmethod
    def parse_text(text):
        """Parses a text by ignoring non ascii characters and replacing \\n with \n.
        Args:
            text (str): Text that will be parsed.
        Returns:
            (str):  A totally compatible ASCII text. Some characters may have been removed."""
        return str(str(text).encode("ascii", "ignore")).replace("\\n","\n")

    @staticmethod
    def to_string(obj):
        """Converts a basic python type to string. Also parses the converted string.
        Args:
            obj (:obj:):    Object to convert to string.
        Returns:
            (str): The parsed string representation of the input object."""
        if isinstance(obj, dict):
            str_obj = '{'
            for key, value in obj.items:
                str_obj += Parser.parse_text(key)+': '+Parser.parse_text(value)+'\n'
            return str_obj + '}'
        else:
            return Parser.parse_text(obj)

class Logger:
    """Logger class. Has the static methods that write the log history of the workspace."""
    @staticmethod
    def log(priority, *messages):
        """Concatenates all the input messages and sends them to the configured handlers of LOG.
        Args:
            priority (str):     Priority of the messages. Lower priority levels are recommended for redundant information,
                                as they won't be shown if a normal level is configured in the LOG.
                                Options: 'debug', 'info', 'warning', 'error', 'critical'.
            *messages (str):    All the messages to write in the log. Separated by commas.
        Raises:
            TypeError:  If the priority argument doesn't match with any of the options."""
        message = ''
        for msg in messages:    message += Parser.to_string(msg)
        priority = priority.lower()

        if 'debug' in priority:         LOG.debug((message))
        elif 'info' in priority:        LOG.info((message))
        elif 'warning' in priority:     LOG.warning((message))
        elif 'error' in priority:       LOG.error((message))
        elif 'critical' in priority:    LOG.critical((message))
        else:                           
            raise TypeError('Invalid priority, accepted strings are: DEBUG | INFO | WARNING | ERROR | CRITICAL')

    @staticmethod
    def exception(*messages):
        """Concatenates the messages, and show the result with the highest level of priority.
        Args:
            *messages (str):    All the messages to write in the log. Separated by comma"""
        Logger.log('CRITICAL', *messages)

    '''def save(self, *messages):
        hour = time.strftime("_%H_%M_%S")
        today = time.strftime("_%d_%m_%Y")
        title = Parser.parse_text(_title)

        file = open("./logs/"+threading.currentThread().getName()+today+".log",'a+')
        file.write("\n=="+title+hour+"==\n")
        if type(data) is dict: #Dictionary with each value being a triplet. From get_all_items
            for key in data.keys():
                file.write(Parser.parse_text(key) + " -> "+ Parser.parse_text(str(data[key].x)) +"\n")
        elif type(data) is list: #From get_item, market item, attribute listings
            for listing in data:
                file.write(str(listing.id)+" - "+str(listing.price/100)+" euros\n")
        else: #plain text
            file.write(Parser.parse_text(data))
        file.write("=====================================\n")
        file.close()


    def save_exception(self, exc):
        self.LOG.error("Error - %s", str(exc))
        hour = time.strftime("_%H_%M_%S")
        today = time.strftime("_%d_%m_%Y")
        data = (str(exc)+traceback.format_exc())

        file = open("./logs/ERROR_"+threading.currentThread().getName()+today+".log",'a+') #Replace to fix OSError
        file.write("\n=="+hour+"==\n")
        file.write(Parser.parse_text(data))
        file.write("=====================================\n")
        file.close()'''