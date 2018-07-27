from UI_Element import UI_Element

class Setting:
    def __init__(self, UI_Element=None):
        self.graphics = UI_Element #Not really an ui element, a subclass of this one

    def get_position(self):
        return self.graphics.get_pos()

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        
class Button_setting(Setting):
    def __init__(self, UI_Element=None, set_of_values=[]):
        super().__init__(UI_Element)
        self.values = set_of_values
        self.index = 0

        #For the sake of writing short code
    def get_value(self):
        return self.values[self.index]

    def hitbox_action(self, mouse_buttons, mouse_pos):
        if mouse_buttons[1]: #This is a tuple, the first one is the left button. Right button was clicked
            self.dec_index()
        else: #left or center button were pressed
            self.inc_index()

    def inc_index(self):
        self.index += 1
        if self.index >= len(self.values):
            self.index = 0

    def dec_index(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.values)-1

class Slider_setting(Setting):
    def __init__(self, UI_Element=None, value=1):
        super().__init__(UI_Element)
        self.value = value

    def get_value(self):
        return self.value

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        #TODO check slider and values of the mouse and shit