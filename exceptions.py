__all__ = ["ScreenNotFoundException", "NoScreensException", "EmptyCommandException", "InvalidGameElementException",
            "BadUIElementInitException", "InvalidUIElementException", "InvalidCommandValueException"]

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

class BadCharacterInitException(Exception):
    pass

class BadPlayersParameter(Exception):
    pass

class BadResizerParamException(Exception):
    pass

class BadCharacterActionException(Exception):
    pass

class BadPlayerTypeException(Exception):
    pass