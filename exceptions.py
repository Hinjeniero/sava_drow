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

class StateNotFoundException(Exception):
    pass

class BadPlayerTypeException(Exception):
    pass

class PlayerNameExistsException(Exception):
    pass

class TooManyElementsException(Exception) :
    pass

class ShapeNotFoundException(Exception):
    pass

class InvalidSliderException(Exception):
    pass

class NotEnoughSpritesException(Exception):
    pass