"""--------------------------------------------
Exception module. Contains all the custom exceptions of the project.
    IpGetter
--------------------------------------------"""

__all__ = ["ScreenNotFoundException", "NoScreensException", "EmptyCommandException", "InvalidGameElementException",
            "BadUIElementInitException", "InvalidUIElementException", "InvalidCommandValueException"]
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

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

class BadSpriteException(Exception):
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
    
class NotEnoughSpaceException(Exception):
    pass

class BadStateException(Exception):
    pass

class TooManyCharactersException(Exception):
    pass

class GameEndException(Exception):
    pass

class SwapFailedException(Exception):
    pass

class ServiceNotAvailableException(Exception):
    pass
class TooManyPlayersException(Exception):
    pass

class ZeroPlayersException(Exception):
    pass

class NotEnoughHumansException(Exception):
    pass

class TooManySurfaces(Exception):
    pass