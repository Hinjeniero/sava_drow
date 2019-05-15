"""--------------------------------------------
dialog_generator module.
Have the following classes:
    DialogGenerator
--------------------------------------------"""
__all__ = ['DialogGenerator']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Selfmade libraries
from strings import MONOSPACED_FONT
from settings import USEREVENTS, PATHS
from obj.ui_element import Dialog, UIElement, SelectableTable
from obj.utilities.colors import WHITE

class DialogGenerator(object):
    """DialogGenerator class. Contains static method to create some prefabbed dialogs that are used 
    extensively across the game."""
    
    @staticmethod
    def create_exit_dialog(id_, size, resolution, text='Are you sure that you want to exit?'):
        """Creates the default exit dialog of the game. It is supposed to be added in main menu.
        Args:
            id_ (String):   Id of this dialog.
            size (Tuple->int, int): Size of the dialog. In pixels.
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            text (String, default='Message'):   Message that will be shown when the dialog is visible (In the middle of it).
        Returns:
            (:obj: Dialog): Dialog created following the input arguments.""" 
        dialog = Dialog(id_+'_exit_dialog', USEREVENTS.DIALOG_USEREVENT, size, resolution, text=text, rows=3, cols=2, texture=PATHS.DIALOG_SILVER, keep_aspect_ratio = False)
        dialog.add_text_element('exit_dialog_text', 'you will lose all your unsaved changes.', dialog.get_cols())
        dialog.add_button(dialog.get_cols()//2, 'Ok', 'ok_yes_exit_already', texture=PATHS.SHORT_GOLD_BUTTON)
        dialog.add_button(dialog.get_cols()//2, 'Cancel', 'no_cancel_false', texture=PATHS.SHORT_GOLD_BUTTON)
        return dialog

    @staticmethod
    def create_input_dialog(id_, size, resolution, *inputs):
        """Creates the default input dialog of the game. It is supposed to be added when we need some information from the user.
        Args:
            id_ (String):   Id of this dialog.
            size (Tuple->int, int): Size of the dialog. In pixels.
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            *inputs (Tuples->(String, String)):    Must follow the schema: tuple(text input box, command inpout box).
        Returns:
            (:obj: Dialog): Dialog created following the input arguments.
        """
        dialog = Dialog(id_+'_input_dialog', USEREVENTS.DIALOG_USEREVENT, size, resolution, rows=(len(inputs)*2)+1, cols=2, texture=PATHS.DIALOG_SILVER, keep_aspect_ratio = False)
        for input_ in inputs:
            dialog.add_text_element('text', input_[0], dialog.get_cols())
            if len(input_) == 2:
                dialog.add_input_box(dialog.get_cols(), '', input_[1], texture=PATHS.SHORT_DARK_GOLD_BUTTON, keep_aspect_ratio=False)
            elif len(input_) == 3:
                dialog.add_input_box(dialog.get_cols(), '', input_[1], texture=PATHS.SHORT_DARK_GOLD_BUTTON, initial_text=input_[2], keep_aspect_ratio=False)
            else:
                raise AttributeError("Too few/many elements per tuple when creating an input dialog.")
        dialog.add_button(dialog.get_cols()//2, 'Send', 'ok_yes_input_already', texture=PATHS.SHORT_GOLD_SHADOW_BUTTON, resize_mode='fill')
        dialog.add_button(dialog.get_cols()//2, 'Cancel', 'no_cancel_false', texture=PATHS.SHORT_GOLD_SHADOW_BUTTON, resize_mode='fill')
        return dialog

    @staticmethod
    def create_table_dialog(id_, command, row_size, resolution, keys, *rows):
        """Creates a default SelectableTable. It is supposed to be added when we need some the user to choose from a lot of rows.
        Args:
            id_ (String):   Id of this dialog.
            command (String):   Command to be triggered when the user picks a row.
            row_size (Tuple->int, int): Size of each row of the table. In pixels.
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            keys (Tuple->Strings):  Keys that will be shown at the top of the table.
            *rows (Tuples->Strings):    Data to be shown on the table, below the first row.
        Returns:
            (:obj: SelectableTable): SelectableTable created following the input arguments.
        """
        table = SelectableTable(id_+'_table_dialog', USEREVENTS.DIALOG_USEREVENT, command, row_size, resolution, keys, *rows, text_font=MONOSPACED_FONT)
        return table

    @staticmethod
    def generate_popups(resolution, *ids_texts, text_size=0.95, text_color=WHITE):
        """Creates popups. This method is designed to produce a lot of popups in one call.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            *ids_texts (Tuples->(String, String)):  Tuples that contain the id and text of each dialog.
                                                    The ammount of created popups is linked directly to how many tuples are received here.
            text_size (float):  Text size proportion. 1 would be the maximum achievable size without getting out of the broders.
            text_color (Tuple->(int, int, int)):    Color of the text of all the popups in RGB/RGBA format.
        Returns:
            (List->:obj: Dialog):   A list containing all the popups generated.
        """
        size = (0.80, 0.10)
        position = tuple(0.5-x/2 for x in size)
        popups = []
        for id_text in ids_texts:
            popups.append(UIElement.factory(id_text[0], None, 0, position, size, resolution, texture=PATHS.LONG_POPUP, keep_aspect_ratio=False,\
                                            text=id_text[1], text_proportion=text_size, text_color=text_color, rows=1))
        return popups

    @staticmethod
    def popups_generator(resolution, text_size=0.95, text_color=WHITE):
        """Creates popups. The same as generate_popups, but done with a generator instead. Created with testing purposes.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            text_size (float):  Text size proportion. 1 would be the maximum achievable size without getting out of the broders.
            text_color (Tuple->(int, int, int)):    Color of the text of all the popups in RGB/RGBA format.
        Returns:
            (Generator):    Generator that can create and return popups in demand.
        """
        size = (0.80, 0.10)
        position = tuple(0.5-x/2 for x in size)
        while True:
            id_text = yield #To receive here, write gen.send(id_text tuple) where gen is this generator wherever
            yield UIElement.factory(id_text[0], None, 0, position, size, resolution, texture=PATHS.LONG_POPUP, keep_aspect_ratio=False,\
                                    text=id_text[1], text_proportion=text_size, text_color=text_color, rows=1)