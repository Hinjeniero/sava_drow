from UI_Element import Slider, Button

class Setting:
    def __init__(self, user_event, UI_Element=None, **kwargs):
        self.graphics = UI_Element #Not really an ui element, a subclass of this one
        self.event = user_event #Event triggered when this element is clicked

    def get_surface(self):
        return self.graphics.image, self.graphics.rect

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        
class Options (Setting):
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
    def __init__(self, UI_Element=None, value=1):
        super().__init__(UI_Element)
        self.value = value

    def get_value(self):
        return self.value

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        #TODO check slider and values of the mouse and shit