from obj.utilities.decorators import run_async
from obj.utilities.utility_box import UtilityBox
from settings import PATHS, STRINGS
from strings import CONFIG_MENU_DIALOGS, GRAPHIC_MENU_DIALOGS, CHARACTERS_DIALOGS, BOARD_DIALOGS
class HelpDialogs(object):
    @staticmethod
    def get_dialog_kwargs(resolution):
        return {'dialog_size': (resolution[0]//3, resolution[0]//2), 'dialog_texture': PATHS.DARK_BRICK}

    @staticmethod
    def add_help_dialogs(menu_id, elements, resolution):
        if 'graphic' in menu_id.lower() or 'video' in menu_id.lower():
            for elem in elements:
                HelpDialogs.add_graphic_menu_dialog(elem, resolution)
        elif 'config' in menu_id.lower():
            for elem in elements:
                HelpDialogs.add_config_menu_dialog(elem, resolution)
        elif 'board' in menu_id.lower():
            for elem in elements:
                HelpDialogs.add_board_dialog(elem, resolution)

    @staticmethod
    @run_async
    def add_graphic_menu_dialog(element, resolution):
        '''dialog_text, animated=False, dialog_texture=None, dialog_size=None, text_color=WHITE, dialog_lines=1, text_outline=1,\
                    text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_font=FONT, **dialog_kwargs'''
        kwargs = HelpDialogs.get_dialog_kwargs(resolution)
        if 'resolution' in element.id:
            element.add_hover_dialog(GRAPHIC_MENU_DIALOGS.RESOLUTION_DIALOG, dialog_lines=UtilityBox.line_number(GRAPHIC_MENU_DIALOGS.RESOLUTION_DIALOG), **kwargs)
        elif 'fps' in element.id:
            element.add_hover_dialog(GRAPHIC_MENU_DIALOGS.FPS_DIALOG, dialog_lines=UtilityBox.line_number(GRAPHIC_MENU_DIALOGS.FPS_DIALOG), **kwargs)
        elif 'fullscreen' in element.id:
            element.add_hover_dialog(GRAPHIC_MENU_DIALOGS.FULLSCREEN_DIALOG, dialog_lines=UtilityBox.line_number(GRAPHIC_MENU_DIALOGS.FULLSCREEN_DIALOG), **kwargs)
        elif 'menu' in element.id and 'bg' in element.id:
            element.add_hover_dialog(GRAPHIC_MENU_DIALOGS.MENU_BG_DIALOG, dialog_lines=UtilityBox.line_number(GRAPHIC_MENU_DIALOGS.MENU_BG_DIALOG), **kwargs)
        elif 'board' in element.id and 'bg' in element.id:
            element.add_hover_dialog(GRAPHIC_MENU_DIALOGS.BOARD_BG_DIALOG, dialog_lines=UtilityBox.line_number(GRAPHIC_MENU_DIALOGS.BOARD_BG_DIALOG), **kwargs)

    @staticmethod
    @run_async
    def add_config_menu_dialog(element, resolution):
        '''dialog_text, animated=False, dialog_texture=None, dialog_size=None, text_color=WHITE, dialog_lines=1, text_outline=1,\
                    text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_font=FONT, **dialog_kwargs'''
        kwargs = HelpDialogs.get_dialog_kwargs(resolution)
        if 'cell' in element.id and 'texture' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.CELL_TEXTURE_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.CELL_TEXTURE_DIALOG), **kwargs)
        elif 'loading' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.LOADING_SCREEN_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.LOADING_SCREEN_DIALOG), **kwargs)
        elif 'player' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.PLAYERS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.PLAYERS_NUMBER_DIALOG), **kwargs)
        elif 'game' in element.id and 'mode' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.GAMEMODE_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.GAMEMODE_DIALOG), **kwargs)
        elif 'size' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.BOARD_SIZE_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.BOARD_SIZE_DIALOG), **kwargs)
        elif 'fill' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.FILLING_ORDER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.FILLING_ORDER_DIALOG), **kwargs)
        elif 'center' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.CENTER_CELL_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.CENTER_CELL_DIALOG), **kwargs)
        elif 'pawn' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.PAWNS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.PAWNS_NUMBER_DIALOG), **kwargs)
        elif 'warrior' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.WARRIORS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.WARRIORS_NUMBER_DIALOG), **kwargs)
        elif 'wizard' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.WIZARDS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.WIZARDS_NUMBER_DIALOG), **kwargs)
        elif 'priestess' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.PRIESTESSES_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.PRIESTESSES_NUMBER_DIALOG), **kwargs)
        elif 'matron' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.MATRON_MOTHERS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.MATRON_MOTHERS_NUMBER_DIALOG), **kwargs)
        elif 'champion' in element.id:
            element.add_hover_dialog(CONFIG_MENU_DIALOGS.HOLY_CHAMPIONS_NUMBER_DIALOG, dialog_lines=UtilityBox.line_number(CONFIG_MENU_DIALOGS.HOLY_CHAMPIONS_NUMBER_DIALOG), **kwargs)


    @staticmethod
    @run_async
    def add_characters_dialogs(characters, resolution):
        for char in characters:
            HelpDialogs.add_character_dialog(char, resolution)                                                                            

    @staticmethod
    @run_async
    def add_character_dialog(char, resolution):
        kwargs = HelpDialogs.get_dialog_kwargs(resolution)
        char_type = char.get_type().lower()
        if 'pawn' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_PAWN, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_PAWN), **kwargs)
        elif 'wizard' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_WIZARD, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_WIZARD), **kwargs)
        elif 'warrior' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_WARRIOR, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_WARRIOR), **kwargs)    
        elif 'priest' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_PRIESTESS, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_PRIESTESS), **kwargs)    
        elif 'matron' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_MATRONMOTHER, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_MATRONMOTHER), **kwargs)    
        elif 'holy' in char_type:
            char.add_hover_dialog(CHARACTERS_DIALOGS.MOVEMENT_HOLYCHAMPION, dialog_lines=UtilityBox.line_number(CHARACTERS_DIALOGS.MOVEMENT_HOLYCHAMPION), **kwargs)

    @staticmethod
    @run_async
    def add_board_dialog(element, resolution):
        kwargs = HelpDialogs.get_dialog_kwargs(resolution)
        if 'fitness' in element.id:
            element.add_hover_dialog(BOARD_DIALOGS.FITNESS_BUTTON, dialog_lines=UtilityBox.line_number(BOARD_DIALOGS.FITNESS_BUTTON), **kwargs)
        elif 'help' in element.id:
            element.add_hover_dialog(BOARD_DIALOGS.HELP_BUTTON, dialog_lines=UtilityBox.line_number(BOARD_DIALOGS.HELP_BUTTON), **kwargs)
        elif 'round' in element.id and 'time' in element.id:
            element.add_hover_dialog(BOARD_DIALOGS.ROUND_TIMER, dialog_lines=UtilityBox.line_number(BOARD_DIALOGS.ROUND_TIMER), **kwargs)    