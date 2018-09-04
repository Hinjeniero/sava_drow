from ui_element import Slider, Button
import pygame
__all__ = ["Options", "Value"]

class Setting (object):
    """Overlay for uielement. Adds funcionality."""

    @staticmethod
    def factory(user_event_id, ui_element, default_values):
        '''Method to decide what subclass to create according to the default values.
        If it's a number, a Value. If its a list of shit, Options.
        Factory pattern method.

        Args:
            user_event_id:
            ui_element:
            default_values:
        
        Raise:
            AttributeError:
        '''
        if type(default_values) is (list or tuple):
            return Options(user_event_id, ui_element, tuple(default_values))
        elif type(default_values) is (int or float):
            return Value(user_event_id, ui_element, float(default_values))
        else:
            return AttributeError("The provided set of default values does not follow any of the existing objects logic.")

    def __init__(self, user_event_id, ui_element):
        self.sprite = ui_element #Not really an ui element, a subclass of this one
        self.__event_id = user_event_id #Event triggered when this element is clicked

    def get_surface(self):
        return self.sprite.image, self.sprite.rect

    def get_value(self):
        pass

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass

    def send_event(self):
        my_event = pygame.event.Event(self.__event_id, value=self.get_value())
        pygame.event.post(my_event)
        
class Options (Setting):
    """Subclass of Setting, specifies a set of options"""
    def __init__(self, user_event_id, ui_element, set_of_values):
        super().__init__(user_event_id, ui_element)
        self.values = set_of_values
        self.index = 0

        #For the sake of writing short code
    def get_value(self):
        return self.values[self.index]

    def hitbox_action(self, mouse_buttons, mouse_pos):
        if mouse_buttons[1]:    self.dec_index() #right click on the mouse
        else:                   self.inc_index() #left or center button were pressed

    def inc_index(self):
        self.index += 1 if self.index < len(self.values) else 0

    def dec_index(self):
        self.index -= 1 if self.index > 0 else len(self.values)-1

class Value (Setting):
    """Subclass of Setting, specifies an associated float value"""
    def __init__(self, user_event_id, ui_element, value):
        super().__init__(user_event_id, ui_element)
        self.value = value

    def get_value(self):
        return self.value

    def hitbox_action(self, mouse_buttons, mouse_pos):
        if type(mouse_pos) is tuple:
            mouse_x = mouse_pos[0]
        elif type(mouse_pos) is pygame.Rect:
            mouse_x = mouse_pos.x
        else:
            raise TypeError("Type of mouse_position must be a Rect or a tuple with the coordinates.")
        self.value = (mouse_x-self.sprite.rect.x) / self.sprite.rect.width
        #TODO redraw the fuckin sprite
        self.sprite.set_slider_position()