from obj.utilities.decorators import run_async
#TODO THE TEXTS THEMSELVES CAN BE LOADED FROM THE STRINGS FILE
class HelpDialogs(object):
    @staticmethod
    def add_help_dialogs(menu_id, elements, resolution):
        if 'graphic' in menu_id:
            for elem in elements:
                HelpDialogs.add_graphic_menu_dialog(elem, resolution)
        elif 'sound' in menu_id:
            for elem in elements:
                HelpDialogs.add_sound_menu_dialog(elem, resolution)
        elif 'config' in menu_id:
            for elem in elements:
                HelpDialogs.add_config_menu_dialog(elem, resolution)
    
    @staticmethod
    @run_async
    def add_graphic_menu_dialog(element, resolution):
        pass
    
    @staticmethod
    @run_async
    def add_sound_menu_dialog(element, resolution):
        pass

    @staticmethod
    @run_async
    def add_config_menu_dialog(element, resolution):
        '''dialog_text, animated=False, dialog_texture=None, dialog_size=None, text_color=WHITE, dialog_lines=1, text_outline=1,\
                    text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_font=FONT, **dialog_kwargs'''
        kwargs = {'dialog_size': (resolution[0]//3, resolution[0]//2)}
        if 'cell' in element.id and 'texture' in element.id:
            text="This setting changes the appearance of the cells. The Basic option is just plain wood, the dark one is some kind of obsidian stone,\
                and the double is slightly darker wood than the basic with a silver ring around it."
            element.add_hover_dialog(text, dialog_lines=4, **kwargs)
        elif 'loading' in element.id:
            text="True shows a loading screen while the board itself is filled with characters, False shows the board and the characters appear as \
                they are created and placed."
            element.add_hover_dialog(text, dialog_lines=4, **kwargs)
        elif 'player' in element.id:
            text="Number of players in the board. 4 players will split the board evenly, leaving less space for characters for each player."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'game' in element.id and 'mode' in element.id:
            text="Each gamemode contains various unmutable settings, apart from Custom. Default spawns a board of 5 levels deep with 16 cells per level. \
                Great Wheel's board has 6 levels and a center cell with special properties."
            element.add_hover_dialog(text, dialog_lines=4, **kwargs)
        elif 'size' in element.id:
            text="Different sizes from the board, with each one delivering different number of levels and cells. Go as follows:\nSmall: 3 levels, 16 cells: 48 total.\
                \nSmall: 3 levels, 16 cells: 48 total.\Medium: 4 levels, 16 cells: 48 total.\nLite: 3 levels, 16 cells: 48 total.\nEtc : 3 levels, 16 cells: 48 total."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'fill' in element.id:
            text="Filling order of the board. Random is not completely random, only adds a bit of randomness when dropping some characters."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'center' in element.id:
            text="True spawns a center cell, False doesn't do it. Pretty explicit."
            element.add_hover_dialog(text, dialog_lines=2, **kwargs)
        elif 'pawn' in element.id:
            text="Number of pawns per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'warrior' in element.id:
            text="Number of warriors per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'wizard' in element.id:
            text="Number of wizards per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'priestess' in element.id:
            text="Number of priestesses per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'matron' in element.id:
            text="Number of matron mothers per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)
        elif 'champion' in element.id:
            text="Number of holy champions per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."
            element.add_hover_dialog(text, dialog_lines=3, **kwargs)

    @staticmethod
    @run_async
    def add_character_dialog(char, resolution):
        pass    
    