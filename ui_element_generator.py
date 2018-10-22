from ui_element import *

#CLOSE_BUTTON = close_button #We could do this if everything weren't inside a class

class UIGenerator (object):
    @staticmethod
    def close_button(id_, user_event_id, window_rect, **params):
        params['text'] = "X"
        size     = (window_rect.width*0.20, window_rect.height*0.10)
        position = (window_rect.width-size[0], 0)      
        return Button(id_, user_event_id, position, size, (0,0), (0, 0),**params)

    @staticmethod
    def red_button_800x100(self, text):
        pass

    @staticmethod
    def red_slider_800x100(self, text):
        pass

    @staticmethod
    def red_button_400x100(self, text):
        pass

    @staticmethod
    def red_slider_400x100(self, text):
        pass

    @staticmethod
    def red_button_custom(self, size, text):
        pass