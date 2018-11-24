#!python3
#coding:utf-8
import threading, traceback, time, logging
__author__  = "David Flaity Pardo - Hinjeniero"

LOGGING_LVL = logging.DEBUG
logging.basicConfig(filename='history.log', level=LOGGING_LVL, format='[%(asctime)s]: %(message)s \n')
std_handler = logging.StreamHandler()   #Needed so logger prints into stdout too, not only in the file
std_handler.level       = LOGGING_LVL     #We don't want everything in screen like in the file, so one lvl up
std_handler.formatter   = logging.Formatter('[%(asctime)s] - %(message)s', "%H:%M:%S") #Format of the stdout handler
logging.getLogger().addHandler(std_handler) #Adding handler
LOG = logging.getLogger()

class Parser:
    @staticmethod
    def parse_text(text):
        return str(str(text).encode("ascii", "ignore")).replace("\\n","\n").replace("b'","").replace('b"',"").replace("'","")

class Logger:
    @staticmethod
    def log(priority, *messages):
        message = ""
        for msg in messages:    message += Logger.__to_string(msg)
        priority = priority.lower()

        if "debug" in priority:         LOG.debug((message))
        elif "info" in priority:        LOG.info((message))
        elif "warning" in priority:     LOG.warning((message))
        elif "error" in priority:       LOG.error((message))
        elif "critical" in priority:    LOG.critical((message))
        else:                           
            raise TypeError("Invalid priority, accepted strings are: DEBUG | INFO | WARNING | ERROR | CRITICAL")
    
    @staticmethod
    def __to_string(obj):
        if isinstance(obj, dict):
            str_obj = "{"
            for key, value in obj.items:
                str_obj += Parser.parse_text(key)+": "+Parser.parse_text(value)+'\n'
            return str_obj + "}"
        else:
            return Parser.parse_text(obj)

    @staticmethod
    def exception(*messages):
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