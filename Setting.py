from UI_Element import Slider, Button
import pygame

class Setting (object):
    """Overlay for uielement. Adds funcionality."""
    def __init__(self, user_event_id, ui_element=None):
        self.graphics = ui_element #Not really an ui element, a subclass of this one
        self.__event_id = user_event_id #Event triggered when this element is clicked

    def get_surface(self):
        return self.graphics.image, self.graphics.rect

    def get_value(self):
        pass

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass

    def send_event(self):
        my_event = pygame.event.Event(self.__event_id, value=self.get_value())
        pygame.event.post(my_event)
        
class Options (Setting):
    """Subclass of Setting, specifies a set of options"""
    def __init__(self, UI_Element=None, set_of_values=[]):
        super().__init__(UI_Element)
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
    def __init__(self, UI_Element=None, value=1):
        super().__init__(UI_Element)
        self.value = value

    def get_value(self):
        return self.value

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        #TODO check slider and values of the mouse and shit