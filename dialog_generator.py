from settings import USEREVENTS
from obj.ui_element import Dialog

class DialogGenerator(object):
    @staticmethod
    def create_exit_dialog(size, resolution, text='Are you sure that you want to exit?'):
        dialog = Dialog('exit_dialog', USEREVENTS.DIALOG_USEREVENT, size, resolution, text=text, rows=3, cols=2)
        dialog.add_text_element('exit_dialog_text', text, dialog.get_cols())
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