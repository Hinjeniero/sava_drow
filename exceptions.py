__all__ = ["ScreenNotFoundException", "NoScreensException", "EmptyCommandException", "InvalidGameElementException"]

class ScreenNotFoundException(Exception):
    pass

class NoScreensException(Exception):
    pass

class EmptyCommandException(Exception):
    pass
    
class InvalidGameElementException(Exception):
    pass

class BadUIElementInitException(Exception):
    pass

class InvalidUIElementException(Exception):
    pass

class InvalidCommandValueException(Exception):
    pass