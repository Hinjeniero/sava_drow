from settings import USEREVENTS, PATHS
from obj.ui_element import Dialog, UIElement
from obj.utilities.colors import WHITE

class DialogGenerator(object):
    @staticmethod
    def create_exit_dialog(size, resolution, text='Are you sure that you want to exit?'):
        dialog = Dialog('exit_dialog', USEREVENTS.DIALOG_USEREVENT, size, resolution, text=text, rows=3, cols=2)
        dialog.add_text_element('exit_dialog_text', 'you will lose all your unsaved changes.', dialog.get_cols())
        dialog.add_button(dialog.get_cols()//2, 'Ok', 'ok_yes_exit_already', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
        dialog.add_button(dialog.get_cols()//2, 'Cancel', 'no_cancel_false', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
        return dialog

    @staticmethod
    def create_input_dialog(size, resolution, *inputs):
        """Tkes double space cuz text and then inputbox of the same size.
        tuple(text input box, command inpout box)"""
        #Dialog
        dialog = Dialog('input_dialog', USEREVENTS.DIALOG_USEREVENT, size, resolution, rows=(len(inputs)*2)+1, cols=2)
        for input_ in inputs:
            dialog.add_text_element('text', input_[0], dialog.get_cols())
            if len(input_) == 2:
                dialog.add_input_box(dialog.get_cols(), '', input_[1], gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
            elif len(input_) == 3:
                dialog.add_input_box(dialog.get_cols(), '', input_[1], gradient=((0, 0, 255, 255),(128, 128, 255, 255)), initial_text=input_[2])
            else:
                raise AttributeError("Too few/many elements per tuple when creating an input dialog.")
        dialog.add_button(dialog.get_cols()//2, 'Send', 'ok_yes_input_already', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
        dialog.add_button(dialog.get_cols()//2, 'Cancel', 'no_cancel_false', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
        return dialog

    @staticmethod
    def generate_popups(resolution, *ids_texts, text_size=0.95, text_color=WHITE):
        size = (0.80, 0.10)
        position = tuple(0.5-x/2 for x in size)
        popups = []
        for id_text in ids_texts:
            popups.append(UIElement.factory(id_text[0], None, 0, position, size, resolution, texture=PATHS.LONG_POPUP, keep_aspect_ratio=False,\
                                            text=id_text[1], text_proportion=text_size, text_color=text_color, rows=1))
        return popups

    @staticmethod
    def popups_generator(resolution, text_size=0.95, text_color=WHITE):
        """THIS IS A TEST"""
        size = (0.80, 0.10)
        position = tuple(0.5-x/2 for x in size)
        while True:
            id_text = yield #To receive here, write gen.send(id_text tuple) where gen is this generator wherever
            yield UIElement.factory(id_text[0], None, 0, position, size, resolution, texture=PATHS.LONG_POPUP, keep_aspect_ratio=False,\
                                    text=id_text[1], text_proportion=text_size, text_color=text_color, rows=1)