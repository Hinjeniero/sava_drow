__version__ = '0.9999'
__author__ = 'David Flaity Pardo'
   
   #Defined with vertical/horizontal choice
   #0 - centered, 1 - left sided, 2 - right sided
    def resize_and_place_elements(self, elements_list, space_between_elements = 0.05, usable_size = 1.00, vertical_offset = 0.00, horizontal_offset = 0.00,\
    alignment_mode = 0, vertical = False):
        size = self.screen.get_size()
        tuple([usable_size*x for x in size]) #Multiplying the entire tuple by a scalar
        width_index=1
        if vertical is False: #Orientation of the elements
            width_index=0
        
        total = 0
        for element in elements_list:
            total += element.hitbox.size[width_index]
            total += element.hitbox.size[width_index]*space_between_elements
        
        proportion = 1
        if total > size[width_index]: #Getting the proportion needed to make everything fit within the window
            proportion = size[width_index]/total

        for element in elements_list: #Actual resizing and reescaling
            element.hitbox.size[width_index] *= proportion #Resizing the important axis
            for i in range (0, len(element.size)):
                if size[i] < element.hitbox.size[i]: #The other axises haven't been resized, and so, they could be out of bounds
                    element.hitbox.size[i] = size[i] - (size[i]*space_between_elements)
            element.surface = pygame.transform.scale(element.surface, element.hitbox.size) #Reisizing the surface
        
        #Now, the placing (Position)

        last_x_position = horizontal_offset
        last_y_position = vertical_offset
        for element in elements_list:
            element.hitbox.pos[width_index] = last_x_position+element.hitbox.size[width_index]*space_between_elements
            last_x_position += element.hitbox.size[width_index]*(1+space_between_elements)
            if alignment_mode is 0:
                element.hitbox.pos[(width_index+1)%2] = ((size[(width_index+1)%2]-element.hitbox.size[(width_index+1)%2])/2) + last_y_position #The other component of the tuple
            elif alignment_mode is 1:
                element.hitbox.pos[(width_index+1)%2] = last_y_position+element.hitbox.size[(width_index+1)%2]*space_between_elements
            else:
                element.hitbox.pos[(width_index+1)%2] = size[(width_index+1)%2]-(element.hitbox.size[(width_index+1)%2]*space_between_elements)
            #element.update_hitbox() #Readjust the hitbox size and position
        #Aaaaand it is done. They still need to be drawed tho

        '''#Pos size transition
        aux = self.timer_option
        if aux > fps: #To create the bounding color effect
            aux = fps-(aux-fps)
        dif = (aux/fps)/3
        print(dif)
        size = tuple([int(x*(1+dif)) for x in element.hitbox.size])'''

            '''#Return the position of the 4 corners of a circle (45º, 135º, 225º, 315º).
    #Returns a list with 4 tuples of position
    def corners_circle (self, circle_radius, circle_pos):
        circles = []
        step = 360/8
        angle = step
        while angle < 360:
            x_pos = circle_pos[0]+circle_radius*math.cos(angle)
            y_pos = circle_pos[1]+circle_radius*math.sin(angle)
            circles.append((x_pos, y_pos))
            angle += step*2
        return circles'''

            def draw_element(self, surface, element_surf, pos):
        pass
        '''for circle in self.circles:
        #rect = pygame.draw.circle(self.screen, circle.color, circle.pos, circle.radius) #Drawing small circles
        #self.fill_gradient(self.screen, (255, 255, 255), (0, 0, 0), rect=rect)

        #surf = gradients.radial(circle.radius*3, (0, 0, 0, 255), (255, 255, 255, 100))
        #self.screen.blit(surf, circle.pos)
        pygame.draw.circle(self.screen, (0,0,0,255), circle.pos, int(circle.radius*small_circles_size)+1) #Black circle under red circle, otherwise, if only the border is drawn, there are some empty pixels
        ptext.draw("Color gradient", (540, 170), color="red", gcolor="purple")
        #gradients.draw_gradient_text(self.screen, "Rabo", 60, (250, 250), (255, 255, 0), (0, 255, 100))'''
    
    #THIS ONLY CREATES THE BASIC HITBOX, WITHOUT SLIDER NOR TEXT!
    def create_surface(self, size, color, border, gradient, startcolor, endcolor, gradient_type, image, border_size, border_color): #UI_Element
        if image:
            surf = pygame.transform.scale(pygame.image.load(image).convert_alpha(), size)
            if border:
                border = pygame.mask.from_surface(surf, 200) #Not using it right now TODO
        else:
            surf = pygame.Surface(size)
            if gradient:
                if gradient_type is 0: #vertical
                    surf = gradients.vertical(size, startcolor, endcolor)
                else: #horizontal
                    surf = gradients.horizontal(size, startcolor, endcolor)
            else:
                surf.fill(color)
            if border and border_size is not 0: #Dont want no existant borders
                pygame.draw.rect(surf, border_color,(0,0)+size, border_size) #Drawing the border in the surface
        #In this point, the only thing left is the text
        return surf

    def update_resolution_low_cost(self, old_resolution, new_resolution): #Menu
        self.background = self.load_background(self.settings["resolution"].current(), background_path=self.bgpath)
        ratio = tuple(y/z for y,z in zip(old_resolution, new_resolution))
        for element in self.showing_menu:
            element.hitbox.size = tuple(int(x*ratio) for x in element.hitbox.size) 
            element.hitbox.pos = tuple(int(x*ratio) for x in element.hitbox.pos) 

class UI_Element: 
    def __init__(self, id, surface, rect):
        self.surface = surface
        self.surface_position = (0, 0)
        self.id = id
        self.hitbox = rect #Contains the position and the size

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    def surface_resize(self):
        new_surf_size = list(self.surface.get_size()) #Copy of the size of the surface
        for surf_axis_size, hitbox_axis_size in zip(new_surf_size, self.hitbox.size):
            if surf_axis_size > hitbox_axis_size:
                ratio = (hitbox_axis_size/surf_axis_size)
                for i in range (0, len(new_surf_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                    new_surf_size[i] = int(new_surf_size[i]*ratio)
        self.surface = pygame.transform.scale(self.surface, tuple(new_surf_size)) #Resizing the surface

    #Sets the surface position on the hitbox
    def set_surface_pos(self, horizontal_offset=0, centering = 0):
        position = list(self.surface_position)
        if centering is 0: #Center
            position[0] = (self.hitbox.size[0]/2) - (self.surface.get_size()[0]/2)
        elif centering is 1: #Left
            position[0] = horizontal_offset
        elif centering is 2:
            position[0] = self.hitbox.size[0]-horizontal_offset
        self.surface_position = tuple(position)

    #MENUUUUUUUUUUUUUUUUUUUUUUU
    #[rows increment font size, columns increment number of letters]
    def fill_font_size_table(self):
        aux = numpy.empty([self.max_font, self.max_font], dtype=(int, 2))
        for i in range (0, self.max_font):
            font = pygame.font.Font(self.font, i)
            txt = ""
            for j in range (0, self.max_font):
                aux[i][j]=font.size(txt)
                txt+="W" #Usually capital w is the biggest letter
        return aux

    def get_setting (self, id_setting): 
        try:
            return self.settings[id_setting].current()
        except KeyError:
            print("The setting "+id_setting+"is not in this menu with id "+self.id)

    def change_active_option(self, index):
        if index != self.active_option_index: #If the option has changed
            self.option_sound.play()
            self.active_option_index = index
            self.timer_option = 0 #Restarting the graphical breathing effect
            if self.active_option_index >= len(self.elements):
                self.active_option_index = 0
            elif self.active_option_index < 0:
                self.active_option_index = len(self.elements)-1

    def max_size_text_old(self, text, max_font, rect_size, font_chosen=None): #To check the max font that would fit
        for i in range (max_font, 0, -1): #Counter from max_text to 0
            font = pygame.font.Font(font_chosen, i)
            size = font.size(text) #Getting the needed size to render this text with i size
            if size[0] < rect_size[0] and size[1] < rect_size[1]: #If the rendered text fits in the rect, we return that font size
                return i

    def max_size_text(self, text, max_font, rect_size): #To check the max font that would fit
        length = len(text)
        for i in range (max_font-1, 0, -1): #Counter from max_text to 0
            text_size = tuple(self.font_size_table[i][length])
            if text_size[0] < rect_size[0] and text_size[1] < rect_size[1]: #If the rendered text fits in the rect, we return that font size
                return i

    def draw_element(self, surface, element, hitbox=True, selected=False, scale_selected_option = 1.2):
        border_width = 2 #in px
        if hitbox:
            if not selected:
                color = element.hitbox.color #We cant use this later since this will mess up the reference, its not a copy
                position = element.hitbox.pos
                size = element.hitbox.size
            else: #active option, this part takes on the grasphical effects load
                #Color smooth transition
                clr = []
                for x in element.hitbox.color:
                    aux = self.timer_option
                    if aux > fps: #To create the bounding color effect
                        aux = fps-(aux-fps)
                    x+=aux*4
                    if x > 255:
                        x = 255
                    clr.append(x)
                color = tuple(clr)

                #Pos smooth transition
                aux = self.timer_option
                if aux > fps:
                    aux = fps-(aux-fps)
                pos = list(element.hitbox.pos)
                pos[0] -= half_fps+(aux/2)
                if pos[0] < 0:
                    pos[0] = 0
                position = tuple(pos)

                size = element.hitbox.size

            border_rect = tuple([x+(border_width*2) for x in size])
            option_surf = pygame.Surface(border_rect)
                
            pygame.draw.rect(option_surf, (0, 0, 255), (0,0)+(border_rect), border_width) #Tuple of 4 components
            filling_rect = (border_width, border_width) + size #Tuple fo 4 components
            pygame.draw.rect(option_surf, color, filling_rect, 0)
            option_surf.set_alpha(255)

            option_surf.blit(element.surface, element.surface_position)
            surface.blit(option_surf, position)
        else: #If not hitbox
            surface.blit(element.surface, element.hitbox.pos)

    #Incrementing the index of the option of the setting. (To use each time a click is detected on the option)
    def change_setting(self, id_setting, index=None, inc_index=None):
        id = id_setting.lower()
        if index is not None:
            self.settings[id].index = index
        elif inc_index is not None:
            self.settings[id].index += inc_index
        self.update_settings()

    #Does all the shit related to the mouse hovering an option
    def mouse_collider(self, mouse_position):
        index = 0
        for ui_element in self.elements: #Mouse_position is a two component tuple
            if mouse_position[0] > ui_element.hitbox.pos[0] and mouse_position[0] < ui_element.hitbox.pos[0]+ui_element.hitbox.size[0] \
            and mouse_position[1] > ui_element.hitbox.pos[1] and mouse_position[1] < ui_element.hitbox.pos[1]+ui_element.hitbox.size[1]:
                return index
            index+=1
        return self.active_option_index #No option is selected, we leave whatever was active

    def test(self):
        loop = True
        while loop:
            clock.tick(fps)
            self.draw()
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())

    '''def create_settings(self, *elements):
        all_settings = []
        for element in elements:
            if type (element) is (list or tuple):
                for subelement in element:
                    all_settings.append(self.__create_setting(subelement))
            elif type(element) is dict:
                for subelement in element.values():
                    all_settings.append(self.__create_setting(subelement))
            else:
                all_settings.append(self.__create_setting(subelement))
        return all_settings'''

    '''#All this follow a scheme that goes like: (horizontal_axis_pos, vertical_axis_pos), (horizontal_axis_size, vertical_axis_size)
    #0 - centered, 1 - left sided, 2 - right sided
    def resize_and_place_elements(self, elements_list, space_between_elements = 0.10, vertical_offset = 0.00, horizontal_offset = 0.00,\
    alignment_mode = 0):
        size = list(screen.get_size()) #Multiplying the entire tuple by a scalar       
        size[1] -= vertical_offset
        total = 0
        for element in elements_list:
            total += element.hitbox.size[1]*(1+space_between_elements) #Adding the size of the height (Since the width will always be the same) and the size of the inter-hitbox space  
        
        if total > size[1]: #Getting the proportion needed to make everything fit within the window
            resize_relation = size[1]/total #The relation is totalsize/myactualsize. totalsize = screen width
            for element in elements_list: #Actual resizing and reescaling
                element_size = list([int(resize_relation*x) for x in element.hitbox.size]) #Multiplying the entire tuple 
                element.hitbox.size = tuple(element_size)
                element.surface_resize()

        #Now, the placing (Position)
        last_y_position = vertical_offset
        for element in elements_list:
            position = list(element.hitbox.pos)
            position[1] = last_y_position
            last_y_position += element.hitbox.size[1]*(1+space_between_elements)
            if alignment_mode is 0:
                position[0] = size[0]/2 - element.hitbox.size[0]/2 + size[0]*horizontal_offset  #The other component of the tuple
            elif alignment_mode is 1:
                position[0] = element.hitbox.size[0] + size[0]*horizontal_offset
            elif alignment_mode is 2:
                position[0] = size[0] - element.hitbox.size[0] - size[0]*horizontal_offset
            element.hitbox.pos = tuple(position)
            element.set_surface_pos()'''

    '''#centering --> 0 = centered, 1 = left, 2 = right   3TODO add accept button and  array of booleans 
    def create_menu(self, logo_path = None, logo_size = (0, 0), title_text = None, title_size = (0, 0), options_list=[], centering = 0, text_color = (255, 255, 255), margin = 0.05):
        res = self.settings["resolution"].current()
        margin = (res[0]*margin, res[1]*margin) #tuple containing the margin
        
        #Establishing the offsets to draw all the components of the menu
        if centering is 0: #Centered
            horizontal_offset = res[0]/2
        elif centering is 1: #Left
            horizontal_offset = margin[0]
        elif centering is 2: #Right
            horizontal_offset = res[0] - margin[0]
        vertical_offset = margin[1]
        
        #Creating logo, with his texture and position at the top
        if logo_path is not None:
            horizontal_offset = res[0]/2 - logo_size[0]/2
            logo_rect = Rectangle(horizontal_offset, vertical_offset, logo_size[0], logo_size[1]) 
            logo_texture = pygame.transform.scale(pygame.image.load(logo_path), logo_rect.size)
            logo = UI_Element('logo', logo_texture, logo_rect)
            self.top_elements.append(logo) #Adding to menu
            vertical_offset = logo.hitbox.pos[1] + logo.hitbox.size[1] + margin[1] #Getting the next free space to draw element

        #Creating title, with the rendered text and his position under the logo
        if title_text is not None:
            if centering is 0: #Centered
                horizontal_offset = res[0]/2 - title_size[0]/2
            #Centering 1 and 2 are already done up there
            title_rect = Rectangle(horizontal_offset, vertical_offset, title_size[0], title_size[1]) #Hitbox of the title text
            size_font = self.max_size_text(title_text, self.max_font, title_rect.size)
            font = pygame.font.Font(self.font, size_font)
            title_surf = font.render(title_text, True, text_color) #This returns a surface. Text will be a surface.
            title_rect.size = (title_rect.size[0], title_surf.get_height())
            title = UI_Element('title_text', title_surf, title_rect)
            self.top_elements.append(title) #Adding to menu
            vertical_offset = title.hitbox.pos[1] + title.hitbox.size[1] + margin[1] #Getting the next free space to draw element

        ui_list = []
        for option in options_list:
            opt_rect = Rectangle(0, 0, res[0]-margin[0]*2, title_size[1]) #Hitbox of the text
            size_font = self.max_size_text(option[1], self.max_font, opt_rect.size) #Using same specs as the title. 
            font = pygame.font.Font(self.font, size_font)
            opt_surf = font.render(option[1], True, text_color) #This returns a surface. Text will be a surface.
            opt_element = UI_Element(option[0], opt_surf, opt_rect)
            ui_list.append(opt_element)

        self.resize_and_place_elements(ui_list, vertical_offset=vertical_offset) #Repositioning and scaling the elements
        for element in ui_list:
            self.elements.append(element)'''        

   def resize(self, new_size):
        new_surf = Resizer.surface_resize(self.image, new_size)
        ratio = new_surf.get_size()/self.rect.size      #Ratio going from 0 to 1 
        #for hitbox_pos, text_pos in zip(self.rect.topleft, self.text_rect.topleft)

    def __adjust_elements(self, resolution):
        total_pixels =  [0, 0]
        total_spaces =  [0, 0]
        last_y =        [0, 0]

        #We want only shallow copies, that way we will modify the sprites directly
        total_sprites = self.static_sprites.sprites().copy()
        total_sprites.extend(self.dynamic_sprites.sprites()) 
        
        #Counting, adding the pixels and comparing to the resolution
        for sprite in total_sprites:
            total_pixels = [sum(x) for x in zip(total_pixels, sprite.rect.size)] 
            total_spaces = [x-y for x,y in zip(sprite.rect.topleft, last_y)]

        total = total_spaces#total = [sum(x) for x in zip(total_pixels, total_spaces)]
        #TODO JUST ASSIGN THE NUMBER OF PIXELS THAT ARE LEFT TO THE POSITIONS.
        print(len(total_sprites))
        print(total_sprites[0].rect.size)
        print(total_pixels)
        print(total)
        #Getting the ratios between total elements and native resolution
        ratios = [x/y for x, y in zip(resolution, total)]

        if any(ratio < 1 for ratio in ratios):                                                          #If any axis needs resizing
            for sprite in total_sprites:#TODO calculate position too, amd make a rect
                position = tuple([x*y for x,y in zip(ratios, sprite.rect.topleft) if x<1])
                size =     tuple([x*y for x,y in zip(ratios, sprite.rect.size) if x<1])
                sprite.generate_object(rect=pygame.Rect(position, size))                #Adjusting size

#UI_Element, button

    def return_active_surface(self):
        overlay = pygame.Surface(self.rect.size).fill(self.mask_color)
        return self.image.copy().blit(overlay, (0,0))
        -
#attributes
        #Regarding animation
        self.speed = 5
        self.mask_color = WHITE
        self.transparency = 0
        self.transparency_speed = 15

    def move(self):    
        self.rect.x += self.speed
        if self.rect.x < self.speed:    self.speed = -self.speed

        self.transparency += self.transparency_speed
        if self.transparency >= 255:    self.transparency_speed = -self.transparency_speed 



        #In draw of board
        for i in range (0, self.lvl_inception-1): #Dont want a circle in the first lvl
            pygame.draw.circle(surface, self.platform.color, self.platform.pos, int(radius), 3) #Drawing big circle
            radius+=ratio
        for lvl, list_of_circles in self.elements.items():
            index = 0
            for circle in list_of_circles:
                pygame.draw.circle(surface, (0,0,0,255), circle.pos, circle.radius+2)
                if circle.surface is not None:
                    if lvl is self.active_circle[0] and index is self.active_circle[1]:
                        pass
                    else:
                        surface.blit(circle.surface, circle.surface_pos)
                index+=1
                
    def run(self): #board
        self.calculate_circles()
        loop = True
        while loop:
            self.clock.tick(self.fps)
            self.draw(screen)
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())                

#game object
    def add_menu(self, id_menu, menu):
        self.menus[id_menu] = menu
        self.showing_menu = menu

    def add_board(self, id_board, board):
        self.boards[id_board] = board
        self.showing_board = board

    def esc_handler(self):
        id_ = self.current_screen().id.lower()
        if ('main' in id_ and 'menu' in id_):
            for i in range(0, len(self.screens)):
                new_id = self.get_screen(i).id.lower()
                if ('main' in new_id and 'board' in new_id):
                    self.screen_index = i
                    break
        elif ('menu' in id_):
            for i in range(0, len(self.screens)):
                new_id = self.get_screen(i).id.lower()
                if ('main' in new_id and 'menu' in new_id):
                    self.screen_index = i
                    break
        elif ('main' in id_ and 'board' in id_):
            for i in range(0, len(self.screens)):
                new_id = self.get_screen(i).id.lower()
                if ('main' in new_id and 'menu' in new_id):
                    self.screen_index = i
                    break

#old update method of sliders
    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        index = random.randint(0, len(self.overlay_color)-1)
        self.overlay_color[index] += self.color_sum

        for i in range (0, len(self.overlay_color)): 
            if self.overlay_color[i] < 0:       self.overlay_color[i] = 0  
            elif self.overlay_color[i] > 255:   self.overlay_color[i] = 255

        if all(color >= 255 for color in self.overlay_color) or all(color <= 0 for color in self.overlay_color):    self.color_sum = -self.color_sum
        self.set_overlay()
        
    #Old methods of Resizer
    @staticmethod
    def __surface_resize(surface, new_size):
        old_size = surface.get_size()
        new_size = list(new_size)
        for new_axis, old_axis in zip(new_size, old_size):
            ratio = (new_axis/old_axis)
            for i in range (0, len(new_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                new_size[i] = int(new_size[i]*ratio)
        print("NMEW"+str(new_size))
        return pygame.transform.scale(surface, tuple(new_size)) #Resizing the surface
    
    @staticmethod
    def __sprite_resize(sprite, new_size):
        old_size = sprite.image.get_size()
        old_position = sprite.rect.topleft
        new_position = list(sprite.rect.topleft)
        ratios = []
        for new_axis, old_axis in zip(new_size, old_size):
            ratio = (new_axis/old_axis)
            for i in range (0, len(new_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                new_size[i] = int(new_size[i]*ratio)
                new_position[i] = int(old_position[i]*ratio)
            ratios.append(ratio)
        sprite.rect.topleft = tuple(new_position)                               #Scaling the rect, pos and size
        sprite.rect.size = tuple(new_size)
        sprite.image = pygame.transform.scale(sprite.image, sprite.rect.size)    #Scaling the surface and size
        return ratios

#CHARACTER
    #THIS NEEDS A FUCKIN BACKTRACKING
    #Map --> graph of booleans
    #paths --> Contain info of all the rooms
    #TODO make sure of the format to return and the format of the input parameters to make a decent implementation
    def generate_paths(self, map, paths, initial_pos):
        possible_paths  = []
        current_path    = []
        checked         = []
        to_check        = [initial_pos]
        step            = 0
        while len(to_check) > 0:
            current_pos = to_check.pop(-1)
            checked.append(current_pos)
            current_path.append(current_pos)
            if len(current_path) is self.movement.dist or current_path[-1] is current_path[0]: #TODO HOW TO CHECK PRIESTESS USE CASES OF THE LVL-moving-and-ending
                self.__add_path(current_path, possible_paths)
                to_check.pop(-1)
                current_path.pop(-1)
            else:
                for cell in map[current_pos]:
                    if cell not in checked and cell not in to_check:
                        if self.valid_mvnt(initial_pos, cell):
                            to_check.append(cell)
            step += 1
        return possible_paths

##Sync method of factory
class Character(pygame.sprite.Sprite):
    @staticmethod
    def factory(player_name, pieces_qty, sprite_size, **sprite_paths):
        characters                          = pygame.sprite.Group()
        if not isinstance(pieces_qty, dict):    raise BadCharacterInitException("pieces_qty must be dictionary, not "+str(type(pieces_qty)))   
        if not isinstance(sprite_paths, dict):  raise BadCharacterInitException("sprite_paths must be dictionary, not "+str(type(sprite_paths)))
        
        limit, counter = 8, 0
        if "pawn" in pieces_qty:            limit = pieces_qty["pawn"]
        while counter < limit:
            name = "pawn_"+str(counter)    
            if "pawn" in sprite_paths:      characters.add(Pawn(player_name, name, sprite_size, sprite_paths["pawn"]))
            else:                           characters.add(Pawn(player_name, name, sprite_size, IMG_FOLDER+"\\pawn"))
            counter+=1
            LOG.log('DEBUG', "Loading character ", name, " of player ", player_name) 

        limit, counter = 4, 0
        if "warrior" in pieces_qty:         limit = pieces_qty["warrior"]
        while counter < limit:
            name = "warrior_"+str(counter) 
            if "warrior" in sprite_paths:   characters.add(Warrior(player_name, name, sprite_size, sprite_paths["warrior"]))
            else:                           characters.add(Warrior(player_name, name, sprite_size, IMG_FOLDER+"\\warrior"))
            counter+=1
            LOG.log('DEBUG',"Loading character ", name, " of player ", player_name)

        limit, counter = 2, 0
        if "wizard" in pieces_qty:          limit = pieces_qty["wizard"]
        while counter < limit:
            name = "wizard_"+str(counter) 
            if "wizard" in sprite_paths:    characters.add(Wizard(player_name, name, sprite_size, sprite_paths["wizard"]))
            else:                           characters.add(Wizard(player_name, name, sprite_size, IMG_FOLDER+"\\wizard"))
            counter+=1
            LOG.log('DEBUG',"Loading character ", name, " of player ", player_name)

        limit, counter = 2, 0
        if "priestess" in pieces_qty:          limit = pieces_qty["wizard"]
        while counter < limit:
            name = "priestess_"+str(counter)
            if "priestess" in sprite_paths: characters.add(Priestess(player_name, name, sprite_size, sprite_paths["priestess"]))
            else:                           characters.add(Priestess(player_name, name, sprite_size, IMG_FOLDER+"\\priestess"))
            counter+=1
            LOG.log('DEBUG',"Loading character ", name, " of player ", player_name)
        return characters
    #TODO make those whiles in a method, this shit repeats a lot of code

    #map is of type numpy, and paths of type 
    def generate_paths(self, circle_number, existing_paths, type_paths, initial_pos): #TODO Initial pos is a pasth and we are passing it as a utple
        print("Searching paths for "+self.id)
        possible_paths  = []    #All solutions
        current_path    = []    #Currebt solutionb
        checked         = []    #Checked already    
        to_check        = [(initial_pos, initial_pos)] #Both are paths type objects. Every objects of us is (path, path)
        step            = 0     #Simply index
        while len(to_check) > 0:
            current_square     = to_check.pop(-1)
            current_path.append(current_square)
            if step is self.movement.dist:
                self.__add_path(current_path, possible_paths)
                current_path.pop(-1)
                current_square  = current_path[-1]
                step            -= 1
            else:
                for i in range (0, len(existing_paths[current_square[1].index])):
                for dest_cell in existing_paths[current_square[1].index]: #Existing paths only contains booleans
                    next_step = (current_square[1], dest_cell)
                    if next_step not in checked and next_step not in to_check:
                        if self.valid_mvnt(initial_pos, dest_cell):
                            to_check.append(next_step)
            if current_square[1] not in to_check[-1][0]:
                current_path.pop(-1)
                current_square = current_path[-1]
                step        -= 1
                #delete last one
            step            += 1
        return possible_paths
    #PRIESTESS IS EASY! Only have to check which cells are in the same lvl and index, and she can move to those if there exists pathss!!!

    #map is of type numpy, and paths of type 
    def generate_paths(self, circle_number, existing_paths, type_paths, initial_pos): #TODO Initial pos is a pasth and we are passing it as a utple
        print("Searching paths for "+self.id)
        possible_paths  = []    #All solutions
        current_path    = []    #Currebt solutionb
        checked         = []    #Checked already    
        to_check        = [(initial_pos, initial_pos)] #Both are paths type objects. Every objects of us is (path, path)
        step            = 0     #Simply index
        while len(to_check) > 0:
            current_square     = to_check.pop(-1)
            current_path.append(current_square)
            if step is self.movement.dist:
                self.__add_path(current_path, possible_paths)
                current_path.pop(-1)
                current_square  = current_path[-1]
                step            -= 1
            else:
                for i in range (0, len(existing_paths[current_square[1].index])):
                for dest_cell in existing_paths[current_square[1].index]: #Existing paths only contains booleans
                    next_step = (current_square[1], dest_cell)
                    if next_step not in checked and next_step not in to_check:
                        if self.valid_mvnt(initial_pos, dest_cell):
                            to_check.append(next_step)
            if current_square[1] not in to_check[-1][0]:
                current_path.pop(-1)
                current_square = current_path[-1]
                step        -= 1
                #delete last one
            step            += 1
        return possible_paths
    #PRIESTESS IS EASY! Only have to check which cells are in the same lvl and index, and she can move to those if there exists pathss!!!
    
    def __assign_quadrant(self, cell, container_center, count_axis=False):
        x, y = cell.rect.center[0], cell.rect.center[1]
        center_x, center_y = container_center[0], container_center[1]
        if 0 < abs(x - center_x) < 2: x = center_x
        if 0 < abs(y - center_y) < 2: y = center_y
        if not count_axis:  quadrant = 0 if (x>=center_x and y<center_y) else 1 if (x>center_x and y>=center_y)\
                            else 2 if (x<=center_x and y>center_y) else 3
        else:               quadrant = 0 if (x>center_x and y<center_y) else 1 if (x>center_x and y>center_y)\
                             else 2 if (x<center_x and y>center_y) else 3 if (x<center_x and y<center_y) else -1
        
        #LOG.log('DEBUG', "Cell with pixel pos x, y => " , x, ", ", y, ", center => ", center_x, ", ", center_y,\
        #", quadrant => ", quadrant, ", cell => ", cell.get_level(), ", ", cell.get_index())
        self.quadrants[quadrant].append(cell)

#POLYGONS

    @staticmethod
    def generate_surface (surf_size, radius, surf_color, use_gradient, start_color, end_color, border, border_size, border_color):
        """Generates a transparent surface with a circle drawn in it (According to parameters).
        
        Args:
            surf_size: Rect or tuple containing the dimensions of the surface (width, height)
            radius: Radius of the drawn circle
            surf_color: Solid color of the circle. 
            use_gradient: True if we want a circle w/ a gradient. Priority over solid colors.
            start_color: Starting color of the gradient. Only if gradient is True.
            end_color: Ending color of the gradient. Only if gradient is True.
            border: True if the circle has a border.
            border_size: Size of the border in pixels.
            border_color: Color of the border. RGBA/RGB format.
        
        Returns:
            A surface containing the circle.
        """
        surf = pygame.Surface(surf_size)
        if use_gradient: surf = gradients.radial(radius, start_color, end_color) 
        else: pygame.draw.circle(surf, surf_color, (radius, radius), radius, 0)
        if border: pygame.draw.circle(surf, border_color,(radius, radius), radius, border_size)
        if type(surf_size) is pygame.Rect:
            return surf, surf_size
        else:       #We need a coordinate to create a Rect, so if the size is a tuple, 0,0 will it be.
            return surf, pygame.Rect((0,0)+surf_size)


    @staticmethod
    def generate_surface(surf_size, image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color):
        """Generates a transparent surface with a rectangle drawn in it (According to parameters).
        The rectangle will leave no transparent pixels, taking up all the surface space.

        Args:
            surf_size: Rect or tuple containing the dimensions of the surface (width, height)
            image: Texture to draw in the surface. Priority over solid colors and gradients.
            surf_color: Solid color of the circle. Only if use_gradient is False.
            use_gradient: True if we want a circle w/ a gradient. 
            start_color: Starting color of the gradient. Only if gradient is True.
            end_color: Ending color of the gradient. Only if gradient is True.
            border: True if the circle has a border.
            border_size: Size of the border in pixels.
            border_color: Color of the border. RGBA/RGB format.
        
        Returns:
            A surface containing the Rectangle.
        #surf = Resizer.resize_same_aspect_ratio(pygame.image.load(image).convert_alpha(), surf_size)
        #if border: border = pygame.mask.from_surface(surf, 200)         #If image needs a border, mask. Not using it right now TODO
        """
        surf_size   = tuple([int(x) for x in surf_size])
        if image:   surf = pygame.transform.smoothscale(pygame.image.load(image).convert_alpha(), surf_size)
        else:
            surf    = pygame.Surface(surf_size)
            if use_gradient:    surf = gradients.vertical(surf_size, start_color, end_color) if gradient_type == 0 else gradients.horizontal(surf_size, start_color, end_color) #Checking if gradient and type of gradient
            else:               surf.fill(surf_color)
            if border and border_size is not 0: pygame.draw.rect(surf, border_color,(0,0)+surf_size, border_size) #Drawing the border in the surface, dont want no existant borders
        
        if type(surf_size) is pygame.Rect:      return surf, surf_size
        else:                                   return surf, pygame.Rect((0,0)+surf_size)
    
#OLD CHARACTER
class Character(AnimatedSprite):
    def __init__(self, my_player, id_, size, sprites_path):
        LOG.log('DEBUG', "Initializing character ", id_, " of player ", my_player)
        super().__init__()
        self.my_master  = my_player
        self.movement   = Restrictions()
        self.files      = {}
        self._sprites   = {"idle"   : [], 
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.big_sprites= {"idle"   : [],
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.masks      = {"idle"   : [],
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.state      = "idle"
        self.index      = 0
        self.counter    = 0
        self.hover      = False
        self.selected   = False
        self.load_sprites(size, sprites_path)
    
    def get_master(self):
        return self.my_master

    def change_size(self, size):
        for list_ in self.sprites.values():     list_.clear()
        for list_ in self.big_sprites.values(): list_.clear()
        for list_ in self.masks.values():       list_.clear()
        for sprite_path in self.files.keys():   self.__add_sprite(sprite_path, size)
        self.rect.size = self.__current_sprite().get_size()

    def move(self): #move(cols, rows, char_in_middle, char_just_near)
        if 0: return True   #Allowed movm
        if 1: return False  #not allowed

    #This method is tested already
    def load_sprites(self, size, sprite_path):
        sprite_images = [sprite_path+'\\'+f for f in listdir(sprite_path) if isfile(join(sprite_path, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                self.__add_sprite(sprite_image, size)
        self.image  = self.__current_sprite()
        self.rect   = pygame.Rect((200, 200), self.image.get_size())
        self.mask   = self.__current_mask()
    
    def __add_sprite(self, path, size=None):
        for action in self.sprites.keys():
            if action in path.lower():
                try:                self.files[path] 
                except KeyError:    self.files[path] = pygame.image.load(path)
                if size is None:    self.sprites[action].append(self.files[path])
                else:               self.sprites[action].append(Resizer.resize_same_aspect_ratio(self.files[path], size))
                self.masks[action].append(pygame.mask.from_surface(self.sprites[action][-1]))
                big_sprite = pygame.transform.smoothscale(self.sprites[action][-1], tuple(int(x*1.25 ) for x in self.sprites[action][-1].get_size()))
                self.big_sprites[action].append(big_sprite)
                return

    def update(self): #Make it bigger (Like when in touch with hitbox, this could be done in board itself)
        self.counter        += 1
        if self.counter is NEXT_SPRITE_COUNTER:
            self.counter    = 0
            self.animate()

    def change_action(self, action):
        try:
            self.sprites[action]
            self.state  = action
            self.index  = 0
            self.image  = self.sprites[action][self.index] #TODO big sprite here too
        except KeyError:
            raise BadCharacterActionException("Character doesn't have the action "+str(action))

    def animate(self):
        #if self.state is not "pick":
        self.index  = 0 if self.index is len(self.sprites[self.state])-1 else self.index+1
        self.image  = self.__current_sprite() if not self.hover else self.__current_big_sprite()
        self.mask   = self.__current_mask()
        #else:   self.index +=1 if self.index < len(self.sprites[self.state])-1 else 0

    def hitbox_action(self, command, value=-1):
        #if  "mouse" in command and "sec" in command:        self.dec_index()
        #elif "mouse" in command and "first" in command:     self.inc_index()
        pass

    def set_selected(self, selected=True):
        self.index  = 0
        if selected: 
            self.state      = "pick"
            self.selected   = True
        else:
            self.state      = "idle"
            self.selected   = False
    
    def is_selected(self):
        return self.selected
    
    def mvnt_possible(self, source, destiny):
        return True
    
    def set_hover(self, active=True):
        if active:  self.image = self.__current_big_sprite()
        else:       self.image = self.__current_sprite()
        self.hover = active

#UI_ELEMENT, TEXT SPRITE
    def set_position(self, source_rect, alignment, offset=(0, 0)):
        if isinstance(source_rect, tuple):  source_rect = pygame.Rect((0, 0), source_rect)
        elif not isinstance(source_rect, pygame.Rect):  raise BadUIElementInitException("Source rect of text sprite must be a tuple or a rect")
        x_pos               = int(source_rect.width*0.02) if alignment is 1 \
            else            source_rect.width-self.image.get_width() if alignment is 2 \
            else            (source_rect.width//2)-(self.image.get_width()//2)
        y_pos               = (source_rect.height//2)-(self.image.get_height()//2)
        self.rect.topleft   = [x+y for x,y in zip(offset, (x_pos, y_pos))]

    def generate(self, text, rect=None):
        if rect is not None and isinstance(rect, pygame.Rect):              self.rect = rect
        elif rect is not None and isinstance(rect, (list, tuple)):          self.rect = pygame.Rect(self.params["position"], rect)
        elif rect is not None:                                              raise BadUIElementInitException("Can't create text sprite, wrong rect")
        self.params['font_size']    = Resizer.max_font_size(text, self.rect.size, self.params['max_font_size'], self.params['font'])
        self.image                  = pygame.font.Font(self.params['font'], self.params['font_size']).render(text, True, self.params['color'])


    def set_text(self, text):   #Longer string, different size must me used
        if len(text) is not len(self.text):
            self.generate(text)
        else:
            self.image  = pygame.font.Font(self.font, self.size).render(text, True, self.color)
            self.rect   = pygame.Rect(self.rect.topleft, self.image.get_size())
        self.text       = text

#Dict  and methods of uielement
    __default_config = {'texture': None,
                        'fill_color': RED,
                        'keep_aspect_ratio': True,
                        'border': True,
                        'border_width': 2,
                        'border_color': WHITE,
                        'fill_gradient': True,
                        'gradient': (LIGHTGRAY, DARKGRAY),
                        'gradient_type': 0,
                        'overlay_color': WHITE
    }

    def draw_text(self, text, font, canvas_rect, text_rect, max_font_size, text_color, alignment):
        text = TextSprite(self.get_id()+"_text", text, text_rect, font=font, max_font_size=max_font_size, text_color=text_color)
        text.set_position(canvas_rect, alignment)
        self.image.blit(text.image, text.rect)

   def generate_image(self):
        '''Generates the self.image surface, adding and drawing all the pieces that form part of the sprite.
        The rect attribute of the pieces after the first one are the relative position over the first sprite (piece).
        Args:       
            None
        Use:
            self.pieces    
        Returns:
            base_surf:  Complex surface containing all the individual sprites in self.pieces. 
        Raise:
            IndexError: Error if the self.pieces list is empty.
        '''
        if len(self.pieces.sprites())<1:        raise InvalidUIElementException("Creating the image of UIElement returned None")
        #surf                                    = pygame.Surface(self.rect.size) #Doesnt handle well transparencies
        #surf = surf.convert_alpha()
        surf = self.pieces.sprites()[0].image
        for sprite in self.pieces.sprites()[1:]:       surf.blit(sprite.image, sprite.rect.topleft)
        return surf

    def generate(self, rect=None, generate_image=True):
        '''Generates or regenerates the object, using the input rect, or the default self.rect.
        Empty the pieces list, and generate and add the pieces using the self.params values.
        This method can be overriden by subclasses, generating and adding different or more sprites.
        Lastly, the generate_image method is called again, and assigned to the self.image attribute.
        Can be used as a fancy and heavy resizer.
        Args:
            rect:           Rect containing the new size and position of the Element. Defaults to None and uses sef.rect.
            generate_image: Flag. If true, self.image is generated again using generate_image().
        Returns:
            Nothing.
        '''
        if rect is not None:    self.rect, self.params["position"], self.params["size"] = rect, rect.topleft, rect.size
        self.pieces.empty()
        self.overlay            = pygame.Surface(self.rect.size) #TODO Not sure if this is the best place, just doing it here
        self.overlay.fill(self.params['overlay_color']) 
        self.pieces.add(Rectangle((0, 0), self.params['size'], self.params['texture'], self.params['color'],\
                                self.params['border'], self.params['border_width'], self.params['border_color'],\
                                self.params['gradient'], self.params['start_gradient'], self.params['end_gradient'], self.params['gradient_type']))
        if generate_image:    
            self.image          = self.generate_image()  
            self.save_state()

    def save_state(self):
        self.image_original  =   self.image.copy()
        self.rect_original   =   self.rect.copy()        

    def load_state(self):
        self.image  =   self.image_original.copy()
        self.rect   =   self.rect_original.copy()

#SLIDER
    def load_state(self): #TODO The fuck the draw text here?? 
        self.image  =   self.image_original.copy()
        self.rect   =   self.rect_original.copy()
        #Since the original image only contains the background text and color, we need to blit the slider and value again
        self.image.blit(self.slider.image, self.slider.rect)    #Blitting the new slider position                                                   #Sending the event with the new value to be captured somewhere else
        if self.params['shows_value']:  self.draw_text(str(self.get_value()), self.params['font'], self.rect,\
                [x//3 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 2)   

#NEW SPrite methods, but wiht offset

    def draw(self, surface, offset=(0, 0)):
        if self.visible:
            position = tuple([x+y for x,y in zip(offset, self.rect.topleft)])
            if self.use_overlay:    self.draw_overlay(surface, offset=offset)
            else:                   surface.blit(self.image, position)
            self.update()

    def draw_overlay(self, surface, offset=(0, 0)):
        surface.blit(self.overlay, tuple([x+y for x,y in zip(offset, self.rect.topleft)]))

#Slider again
    def draw_slider_overlay(self, color):  #This gets calculated in each frame, this is not necessary
        topleft         = (int(self.value*self.rect.width)-self.rect.height//6, 0)
        center          = (int(self.value*self.rect.width), self.rect.height//2)
        overlay_rect    = pygame.Rect(topleft, (self.rect.height//3, self.rect.height))
        if self.params['slider_type'] is 0:     pygame.draw.circle(self.image, color, center, self.rect.height//2)
        elif self.params['slider_type'] is 1:   pygame.draw.ellipse(self.image, color, overlay_rect)
        else:                                   pygame.draw.rect(self.image, color, overlay_rect)

#New slider
    def draw(self, surface):
        if self.use_overlay:
            self.use_overlay = False #Doing this so we don't draw the default overlay
            super().draw(surface)
            self.use_overlay = True
            self.draw_overlay(surface, UtilityBox.random_rgb_color())
        else:
            super().draw(surface)

#MENU OLD MAIN
#List of (ids, text)
if __name__ == "__main__":
    #Variables
    resolution = (1280, 720)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    timeout = 20

    #Create elements
    sli = UiElement.factory("slider1_command_action", pygame.USEREVENT, (10,10), (800, 100), (0.2))
    but = UiElement.factory("button1_command_action", pygame.USEREVENT+1, (10, 160), (800, 100), (0, 10, 20, 30, 40))
    sli2 = UiElement.factory("slider2_command_action",pygame.USEREVENT+2, (10, 310), (800, 100), (0), text="Slider")
    but2 = UiElement.factory("button2_command_action",pygame.USEREVENT+3, (10, 460), (800, 100), ((50, 60, 70, 80)), text="Button")
    sli3 = UiElement.factory("slider3_command_action",pygame.USEREVENT+4, (10, 960), (800, 100), (1), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UiElement.factory("button3_command_action",pygame.USEREVENT+5, (10, 1110), (800, 100), ((90, 100, 110)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UiElement.factory("slider4_command_action",pygame.USEREVENT+6, (10, 1260), (800, 100), (0.8), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UiElement.factory("button4_command_action",pygame.USEREVENT+7, (10, 1410), (800, 100), (("platano", "naranja", "orange", "ouranch")), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    
    #Create Menu
    menu = Menu("MainMenu", pygame.USEREVENT, resolution, (True, 0), sli, but, sli2, but2, sli3, but3, sli4, but4)
    
    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        menu.draw(screen, clock=clock)       #Drawing the sprite group
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            elif event.type >= pygame.USEREVENT:
                print("Received event number "+str(event.type)+", with value "+str(event.value)+ ", with command "+str(event.command))
            if loop:            #If not exit yet                        
                menu.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())

#OLD MAIN of UI ELEMENT:

if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)
    #Create elements DEPRECATED
    sli = UIElement.factory(pygame.USEREVENT+1, (10,10), (400, 100), (0.80, 0.10), (0.2))
    but = UIElement.factory(pygame.USEREVENT+2, (10, 210), (400, 100), (0.80, 0.10), (30, 40))
    sli2 = UIElement.factory(pygame.USEREVENT+3, (10, 410), (400, 100), (0.80, 0.10), (0.2), text="Slider")
    but2 = UIElement.factory(pygame.USEREVENT+4, (10, 610), (400, 100), (0.80, 0.10), ((30, 40)), text="Button")
    sli3 = UIElement.factory(pygame.USEREVENT+5, (510, 10), (400, 100), (0.80, 0.10), (0.2), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UIElement.factory(pygame.USEREVENT+6, (510, 210), (400, 100), (0.80, 0.10), ((30, 40)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UIElement.factory(pygame.USEREVENT+7, (510, 410), (400, 100), (0.80, 0.10), (0.2), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UIElement.factory(pygame.USEREVENT+8, (510, 610), (400, 100), (0.80, 0.10), ((30, 40)), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    testsuite.add_elements(sli, but, sli2, but2, sli3, but3, sli4, but4)
    testsuite.loop(seconds = timeout)
#Character
    def change_size(self, size):
        for list_ in self.sprites.values():     list_.clear()
        for list_ in self.big_sprites.values(): list_.clear()
        for list_ in self.masks.values():       list_.clear()
        for sprite_path in self.files.keys():   self.__add_sprite(sprite_path, size)
        self.rect.size = self.__current_sprite().get_size()

    def move(self): #move(cols, rows, char_in_middle, char_just_near)
        if 0: return True   #Allowed movm
        if 1: return False  #not allowed

    #This method is tested already
    def load_sprites(self, size, sprite_path):
        sprite_images = [sprite_path+'\\'+f for f in listdir(sprite_path) if isfile(join(sprite_path, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                self.__add_sprite(sprite_image, size)
        self.image  = self.__current_sprite()
        self.rect   = pygame.Rect((200, 200), self.image.get_size())
        self.mask   = self.__current_mask()
    
    def __add_sprite(self, path, size=None):
        for action in self.sprites.keys():
            if action in path.lower():
                try:                self.files[path] 
                except KeyError:    self.files[path] = pygame.image.load(path)
                if size is None:    self.sprites[action].append(self.files[path])
                else:               self.sprites[action].append(Resizer.resize_same_aspect_ratio(self.files[path], size))
                self.masks[action].append(pygame.mask.from_surface(self.sprites[action][-1]))
                big_sprite = pygame.transform.smoothscale(self.sprites[action][-1], tuple(int(x*1.25 ) for x in self.sprites[action][-1].get_size()))
                self.big_sprites[action].append(big_sprite)
                return

  def animate(self):
        #if self.state is not "pick":
        self.index  = 0 if self.index is len(self.sprites[self.state])-1 else self.index+1
        self.image  = self.__current_sprite() if not self.hover else self.__current_big_sprite()
        self.mask   = self.__current_mask()
        #else:   self.index +=1 if self.index < len(self.sprites[self.state])-1 else 0
    
    def set_selected(self, selected=True):
        self.index  = 0
        if selected: 
            self.state      = "pick"
            self.selected   = True
        else:
            self.state      = "idle"
            self.selected   = False

    def update(self): #Make it bigger (Like when in touch with hitbox, this could be done in board itself)
        self.counter        += 1
        if self.counter is NEXT_SPRITE_COUNTER:7
            self.counter    = 0
            self.animate()

    '''@staticmethod
    def AAfilledRoundedRect(surface, rect, color, radius=0.4):

        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4)

        surface : destination
        rect    : rectangle
        color   : rgb or rgba
        radius  : 0 <= radius <= 1
        """

        rect         = Rect(rect)
        color        = Color(*color)
        alpha        = color.a
        color.a      = 0
        pos          = rect.topleft
        rect.topleft = 0,0
        rectangle    = Surface(rect.size,SRCALPHA)

        circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
        draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
        circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

        radius              = rectangle.blit(circle,(0,0))
        radius.bottomright  = rect.bottomright
        rectangle.blit(circle,radius)
        radius.topright     = rect.topright
        rectangle.blit(circle,radius)
        radius.bottomleft   = rect.bottomleft
        rectangle.blit(circle,radius)

        rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
        rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

        rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
        rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

        return surface.blit(rectangle,pos)'''
#OLD TREANS POATHS
        '''spr = Rectangle((self.platform.rect.centerx-self.platform.rect.width//2, self.platform.rect.centery), (self.platform.rect.width, 4))
        offset = (360//self.params['circles_per_lvl'])*self.params['initial_offset']
        self.trans_paths.add(*UtilityBox.rotate(spr, 360//self.params['number_of_paths'], self.params['number_of_paths'], offset))
        LOG.log('DEBUG', "Generated middle paths in board ", self.id)'''#TODO MAKE THIS A REAL BROOO'''

#BOARD AGAIN
    def generate_inter_path(self, index):
        point_list = []
        for i in range(self.params['max_levels']-1, 0, -1):
            point_list.append(self.get_cell(i, index).center)
        point_list.append(self.get_cell(0, self.__get_inside_cell(index)).center) #Final point
        return UtilityBox.bezier_surface(*(tuple(point_list)))

    def generate_inter_paths(self):
        self.__adjust_number_of_paths()
        for i in range(0, self.params['circles_per_lvl']):
            if (i+1)%self.params['inter_path_frequency'] is 0:
                self.trans_paths.add(self.generate_trans_path(i)) #HAVE TO ADD SET CANVAS SIZE FUNCIONALITY

    def __get_quadrant(self, cell, container_center, count_axis=False):
        x, y = cell.rect.center[0], cell.rect.center[1]
        center_x, center_y = container_center[0], container_center[1]
        if 0 < abs(x - center_x) < 2: x = center_x
        if 0 < abs(y - center_y) < 2: y = center_y
        if not count_axis:  quadrant = 0 if (x>=center_x and y<center_y) else 1 if (x>center_x and y>=center_y)\
                            else 2 if (x<=center_x and y>center_y) else 3
        else:               quadrant = 0 if (x>center_x and y<center_y) else 1 if (x>center_x and y>center_y)\
                             else 2 if (x<center_x and y>center_y) else 3 if (x<center_x and y<center_y) else -1
        return quadrant

   def __map_enabled_paths(self):
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl'], 
        #paths, offset = self.params['number_of_paths'], self.params['initial_offset']
        
        #Connecting first level among themselves and to the outside of the next lvls
        for x in range(0, circles):
            limit = 4
            if x >= limit:   self.enabled_paths[x][x] = None #Non existant cell
            else:       
                if x+1 is limit:    self.enabled_paths[0][limit-1], self.enabled_paths[limit-1][0] = True, True #End of the circle
                else:               self.enabled_paths[x][x+1], self.enabled_paths[x+1][x] = True, True         #Adyacent
                #Exists and connected with oneself
                self.enabled_paths[x][x] = True                                                                 
                #Mapping to outside
                outside_connected = self.__get_outside_cells(x)
                for connected in outside_connected:
                    self.enabled_paths[x][connected], self.enabled_paths[connected][x] = True, True
                    #Connects the rest of the circles with all the external ones through this path
                    for l in range(connected, circles*(lvls-1), circles): 
                        self.enabled_paths[l][l+circles], self.enabled_paths[l+circles][l] = True, True

        #Rest of the connections
        for x in range(1, lvls):
            for y in range(0, circles):
                index = x*circles + y
                #If last of the circle
                if y+1 is circles: #THe end of the circle connnected to the start
                    self.enabled_paths[index][x*circles], self.enabled_paths[x*circles][index] = True, True
                else: #Connecting adyacent
                    self.enabled_paths[index][index+1], self.enabled_paths[index+1][index] = True, True
                #Conencting oneself
                self.enabled_paths[index][index] = True
            
        LOG.log('DEBUG', "Paths of this map: \n", self.enabled_paths) 

    def __map_distances(self): #TODO parse distances in the opposite path (0->15 is not 15, its 1 because its a circle)
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl'], 
        #paths, offset = self.params['number_of_paths'], self.params['initial_offset']
        #Distances first level among themselves
        for x in range(0, circles):
            limit = 4 #limit of the first lvl
            if x < limit:
                for o in range(0, limit): #In the same lvl
                    self.distances[x][o], self.distances[o][x] = abs(o-x), abs(o-x)
                #Connects the rest of the circles with all the external ones through this path 
                outside_connected = self.__get_outside_cells(x)
                for n in range(0, lvls-1):
                    if n > 0:  orig_index = outside_connected + (n-1)*circles
                    else:           orig_index = x
                    for m in range(n, lvls-1):
                        dest_index = outside_connected + m*circles
                        dist = math.trunc(abs(dest_index-orig_index)/circles)
                        self.distances[orig_index][dest_index], self.distances[dest_index][orig_index] = dist, dist
        #Rest of the distances
        for x in range(1, lvls):
            for y in range(0, circles):
                init_index = x*circles + y      
                for z in range(y, circles):
                    index = x*circles + z
                    self.distances[init_index][index], self.distances[index][init_index] = abs(init_index-index), abs(init_index-index)

        self.__parse_two_way_distances()
        LOG.log('DEBUG', "Distances of this map: \n", self.distances)  

#The only purpose of this class is to organize the shit inside characters a little but better
#PLAYER
class Restrictions(object):
    def __init__(self, max_dist=1, move_along_lvl = False, move_along_index = False, bypass_allies=True, bypass_enemies=True, approach_enemies=False):
        self.dist               = max_dist          #Max spaces that a char can move
        self.only_same_lvl      = move_along_lvl    #If only can move along the same level
        self.only_same_index    = move_along_index  #If only can move along the same index
        self.bypass_allies      = bypass_allies     #If can move bypassing allies in a cell
        self.bypass_enemies     = bypass_enemies	#If can move bypassing enemies in a cell
        self.approach_enemies   = approach_enemies  #If can only move in a way that will approach him to enemies

    #map is of type numpy, and paths of type 
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos): #TODO Initial pos is a pasth and we are passing it as a utple
        print("Searching paths for "+self.id)
        possible_paths  = []    #All solutions
        current_path    = []    #Currebt solutionb
        checked         = []    #Checked already    
        to_check        = [(initial_pos, initial_pos)] #Both are paths type objects. Every objects of us is (path, path)
        #LOG.log('DEBUG', "Initial lenght of to check is ", len(to_check))
        while len(to_check) > 0:
            current_square     = to_check.pop(-1)
            current_path.append(current_square)
            #LOG.log('DEBUG', '---------------')
            #LOG.log('DEBUG', "BEFORE: Lenght of to check is ", len(to_check))
            #IF we already have a path that is the max distance
            if len(current_path)-1 is self.movement.dist:
                #LOG.log('DEBUG', 'LEnght of current path ', [(x[0].pos, x[1].pos) for x in current_path], "Is the distance")
                self.add_path(current_path, possible_paths)
                current_path.pop(-1)
                current_square  = current_path[-1]
            else:
                #For every cell possibly connected to the actual one
                for i in range (0, len(existing_paths[current_square[1].index])):   #Existing paths only contains booleans
                    if existing_paths[current_square[1].index][i]\
                    and i is not current_square[1].index:                               #If actually connected (The bool is Tr)                
                        dest_cell = board_map[i]                                            #Assigning the cell using the index
                        next_step = (current_square[1], dest_cell)                          #Creating the tuple step (init cell -> dest cell)
                        if next_step not in checked and next_step not in to_check:          #If we have not done this step and dont have it already queued 
                                if self.valid_mvnt(next_step):   to_check.append(next_step)     #If the step is valid for the character restrictions, append the step
            #If our cell is not connected to the last one appended to check, we have to regress one more step in this backtracking
            #LOG.log('DEBUG', "AFTER: Lenght of to check is ", len(to_check))
            while len(to_check) > 0 and current_square[1] is not to_check[-1][0]:
                #LOG.log('DEBUG', "if ", current_square[1].pos, " is not ", to_check[-1][0].pos, ", entered")
                current_path.pop(-1)
                current_square = current_path[-1]
        return possible_paths

    def add_path(self, path_to_add, final_list):
        path = []
        for element in path_to_add:
            if isinstance(element, (tuple, list)):    
                if isinstance(element[0], tuple): #Nested tuple
                    path.append(tuple(x for x in element[0]))
                elif isinstance(element[0], Path):
                    path.append(tuple(x for x in element[1].pos))
                elif isinstance(element, (float, int)):   
                    path.append(element)
            elif isinstance(element, Path):         path.append(tuple(x for x in element.pos))
            elif isinstance(element, (float, int)):   path.append(element)
        LOG.log('DEBUG', "PATH FOUND! ", path)
        final_list.append(path)

    def valid_mvnt(self, movement):
        init_pos, dest_pos = movement[0], movement[1]
        if init_pos is not dest_pos:
            if not self.movement.bypass_enemies and dest_pos.has_enemy():
                return False 
            if not self.movement.bypass_allies and dest_pos.has_ally():
                return False
            if (init_pos.get_lvl() is not dest_pos.get_lvl() and self.movement.move_in_same_lvl)\
            and (init_pos.get_index() is not dest_pos.get_index() and self.movement.move_in_same_index):
                return False
        return True

    @staticmethod
    def factory(player_name, pieces_qty, sprite_size, canvas_size, **sprite_paths):
        LOG.log('INFO', "----Factory, making ", player_name, " characters----")
        if not isinstance(pieces_qty, dict):    raise BadCharacterInitException("pieces_qty must be dictionary, not "+str(type(pieces_qty)))   
        if not isinstance(sprite_paths, dict):  raise BadCharacterInitException("sprite_paths must be dictionary, not "+str(type(sprite_paths)))
        characters                          = pygame.sprite.Group()
        threads                             = []

        path, number_of = IMG_FOLDER+"\\pawn", 8
        if "pawn" in pieces_qty:            number_of   = pieces_qty["pawn"]
        if "pawn" in sprite_paths:          path        = sprite_paths["pawn"]
        threads.append(Character.__char_loader(Pawn, characters, number_of, player_name, "pawn", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\warrior", 4
        if "warrior" in pieces_qty:         number_of   = pieces_qty["warrior"]
        if "warrior" in sprite_paths:       path        = sprite_paths["warrior"]
        threads.append(Character.__char_loader(Pawn, characters, number_of, player_name, "warrior", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\wizard", 2
        if "wizard" in pieces_qty:          number_of   = pieces_qty["wizard"]
        if "wizard" in sprite_paths:        path        = sprite_paths["wizard"]
        threads.append(Character.__char_loader(Wizard, characters, number_of, player_name, "wizard", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\priestess", 1
        if "priestess" in pieces_qty:       number_of   = pieces_qty["priestess"]
        if "priestess" in sprite_paths:     path        = sprite_paths["priestess"]       
        threads.append(Character.__char_loader(Priestess, characters, number_of, player_name, "priestess", (0, 0), sprite_size, canvas_size, path))

        for t in threads:
            t.join()        #Threading.join
        LOG.log('INFO', "----Factory, done making ", player_name, " characters----")
        return characters

#PAWN
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos):
        print("POSITION "+str(initial_pos.index))
        print("INITIAL DISTANCES")
        initial_distances   = self.__generate_enemies_distances(distance_map, board_map, initial_pos.index)
        unfiltered_paths    = super().generate_paths(existing_paths, board_map, distance_map, initial_pos)
        #print(unfiltered_paths)
        if len(initial_distances) > 0:    #If there is a direct path possible towards an enemy
            for i in range(0, len(unfiltered_paths)):   #For each possible basic path
                dest_pos = None
                for cell in board_map.values():

                    if unfiltered_paths[i][-1] == (cell.get_lvl(), cell.get_index()):
                        dest_pos = cell
                        break
                print("FINAL DISTANCES IN DESTINY "+str(cell.index))
                final_distances = self.__generate_enemies_distances(distance_map, board_map, dest_pos.index)

                #This type of if works because the key is a basic integer, it wouldn't otherwise
                #If there is no less distance with any of the enemies, this path is no good
                delete_path = True
                for key in initial_distances.keys():
                    try:
                        if final_distances[key] < initial_distances[key]: delete_path = False
                    except KeyError:    #This due to the destiny having no connnection to a cell that the start_pos did have.
                        continue
                if delete_path:
                    print("DELETING PATH") 
                    del unfiltered_paths[i]
                    i+=1
        #print(unfiltered_paths)
        return unfiltered_paths #TODO FIX THIS SHIT

    #IN WHERE THE HELL IM CHECKING FOR ENEMIES, WHAT THE FUCK DOES THIS SHIT DO???? 
    def __generate_enemies_distances(self, distance_map, board_map, position):
        distances_to_enemies = {}
        cells_with_enemies = [cell.index for cell in board_map.values() if (cell.index is not position and cell.has_enemy())]
        for cell in board_map.values(): print(cell.index + " has enemy "+str(cell.has_enemy()) + ", ally "+str(cell.has_ally()))
        print(len(cells_with_enemies))
        for cell in cells_with_enemies: print("ENEMIE IN "+str(cell.index))
        raise Exception("dfd")
        if distance_map[position][i] > 0: #Exists direct path to that shit (Same level or big circle [rank or file])
            try:
                if distance_map[position][i] < distances_to_enemies[i]:
                    distances_to_enemies[i] = distance_map[position][i]
            except KeyError:
                distances_to_enemies[i] = distance_map[position][i]
        print(distances_to_enemies)
        return distances_to_enemies

    def copy_sprite(self, new_size, *sprites):
        sprites_copy = []
        for sprite in sprites:
            spr = pygame.sprite.Sprite()
            spr.image, spr.rect = sprite.image.copy(), sprite.rect.copy()
            sprites_copy.append(spr)
        return sprites_copy

#Board main
#List of (ids, text)
if __name__ == "__main__":
    #Variables
    resolution = (1024, 1024)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    timeout = 20
    #Create Board
    game = Board("testboard", pygame.USEREVENT, resolution)    
    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        game.draw(screen, clock=clock)       #Drawing the sprite group
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            elif event.type >= pygame.USEREVENT:
                print("Received event number "+str(event.type)+", with value "+str(event.value))
            if loop:            #If not exit yet                        
                game.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())

    #Doesnt work propperly
    def __get_outside_cells(self, index):
        """Same, but for the outside cells."""
        cells=[]
        space_between_inter_paths = int((self.params['circles_per_lvl']//4)*(1/self.params['inter_path_frequency']))
        i = (self.params['circles_per_lvl']//4)-1
        for _ in range(0, (self.params['circles_per_lvl']//4)//self.params['inter_path_frequency']):
            cells.append(i+index*(self.params['circles_per_lvl']//4))
            i -= space_between_inter_paths
        return tuple(cells)

#Character
    def valid_mvnt(self, movement):
        init_pos, dest_pos = movement[0], movement[1]
        if init_pos is not dest_pos:
            if not self.movement.bypass_enemies and dest_pos.has_enemy():
                return False 
            if not self.movement.bypass_allies and dest_pos.has_ally():
                return False
            if (init_pos.get_lvl() is not dest_pos.get_lvl() and self.movement.move_in_same_lvl)\
            and (init_pos.get_index() is not dest_pos.get_index() and self.movement.move_in_same_index):
                return False
        return True

#Priestess
    #No need for a backtracking in priestess, only two steps.
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos):
        possible_paths  = []    #All solutions
        for i in range (0, len(existing_paths[initial_pos.index])):
            try:
                if i is not initial_pos.index\
                and distance_map[initial_pos.index][i] > 0:
                            self.add_path([initial_pos, board_map[i]], possible_paths)
            except KeyError:    #Due to the difference in index, due to the different number of circles between levels
                continue
        return possible_paths

#Quadrant
    def __sort_cell(self, cell, *cells):
        """Sort a Cell, and classify it in border or center. Checks the level and index of the Cell,
        and check every other cell."""
        self.cells.add(cell)
        less_lvl, more_lvl, less_index, more_index = False, False, False, False
        for other_cell in cells:
            if all((less_lvl, more_lvl, less_index, more_index)): 
                self.center.add(cell)
                return
            elif other_cell is not cell:
                if other_cell.get_level() < cell.get_level():   less_lvl    = True
                elif other_cell.get_level() > cell.get_level(): more_lvl    = True
                if other_cell.get_index() < cell.get_index():   less_index  = True
                elif other_cell.get_index() > cell.get_index(): more_index  = True
        self.border.add(cell)

#utility_box

    @staticmethod
    def set_curved_corners_rect(surface, radius=None):   #If we have the rect we use it, if we don't, we will get the parameters from the surface itself
        if radius is None:  radius = int(surface.get_width*0.10)
        clrkey = (254, 254, 254)                    #colorkey
        surface.set_colorkey(clrkey)                #A strange color that will normally never get used. Using this instead of transparency per pixel cuz speed
        width, height = surface.get_size()
        UtilityBox.__set_corner_rect(surface, (0, 0), (radius, radius), radius, clrkey)                         #TOPLEFT corner
        #UtilityBox.__set_corner_rect(surface, (width-radius, 0), (width, radius), radius, clrkey)               #TOPRIGHT corner
        #UtilityBox.__set_corner_rect(surface, (0, height-radius), (radius, height), radius, clrkey)             #BOTTOMLEFT corner
        #UtilityBox.__set_corner_rect(surface, (width-radius, height-radius), (width, height), radius, clrkey)   #BOTTOMRIGHT corner

    @staticmethod  
    def __set_corner_rect(surface, start_range, end_range, radius, clrkey):
        step = [1 if start >= end else -1 for start, end in zip(start_range, end_range)]
        x = start_range[1]
        for i in range(start_range[0], end_range[0], step[0]):
            for j in range(x, end_range[1], step[1]):
                if UtilityBox.EUCLIDEAN_DISTANCES[i][j] < radius:
                    surface.set_at((i, j), clrkey)
                    surface.set_at((j, i), clrkey)
            x+=step[1]

#utilitybox

    @staticmethod
    def texturize_surface(size, source_surf, centered=False):
        if type(source_surf) is pygame.Surface: surf = source_surf.copy()
        elif type(source_surf) is str:          surf = pygame.image.load(source_surf)
        else:                                   raise TypeError("Fill can only work with an image path or a surface")
        ratios = [x/y for x, y in zip(size, surf.get_size())]
        if any(ratio > 1 for ratio in ratios):
            factor = max(ratios)
            surf = pygame.transform.smoothscale(surf, tuple([int(axis*factor) for axis in surf.get_size()]))
        result = pygame.Surface(size)
        if centered:    result.blit(surf, (0, 0), pygame.Rect(surf.get_rect().center, size))
        else:           result.blit(surf, (0, 0), pygame.Rect((0, 0), size))
        return result

    @staticmethod
    def load_background(size, background=None):
        """Returns a surface with the size of the screen. That surface can be a """
        if background is None: 
            return gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) 
        return UtilityBox.texturize_surface(size, background)

    @staticmethod
    def texturize_surface(size, source_image):
        if isinstance(source_image, str):
            source_image = pygame.image.load(source_image) 
        return Resizer.resize_same_aspect_ratio(source_image, size)

#Menu
    def set_resolution(self, resolution):
        super().set_resolution(resolution)
        #Regenerate elements
        for sprite in self.static_sprites.sprites():    sprite.set_canvas_size(resolution)
        for sprite in self.dynamic_sprites.sprites():   sprite.set_canvas_size(resolution)
        #if self.have_dialog():      self.dialog.sprite.generate(rect=sprite.get_rect_if_canvas_size(resolution))
        self.generate(centering=self.params['do_align'], alignment=self.params['alignment'])

    def add_elements(self, *elements, overwrite_eventid = False):
        for element in elements:
            if type(element) is list:
                for subelement in element:
                    self.__add_element(subelement, overwrite_eventid=overwrite_eventid)
            elif type(element) is dict:
                for subelement in element.values():
                    self.__add_element(subelement, overwrite_eventid=overwrite_eventid)
            else:
                self.__add_element(element, overwrite_eventid=overwrite_eventid)

    def __add_element(self, element, overwrite_eventid = False):
        '''Decides whether to add the element to the static or the dynamic elements
        based on the type of the element. Afterwards addes it to the chosen one.
        
        Args: 
            element: element to add'''
        if overwrite_eventid is True:               element.set_event(self.event_id)
        #After that
        if issubclass(type(element), UIElement):    self.dynamic_sprites.add(element)
        elif type(element) is pygame.Surface:       self.static_sprites.add(element) #TODO poorly done this one, surface cant be added to this shit
        else:                                       raise TypeError("Elements should be a pygame.Surface, or an ui_element subclass.") 

    def __center_elements(self, alignment='center'):
        self.__center_sprites(self.static_sprites, alignment=alignment)
        self.__center_sprites(self.dynamic_sprites, alignment=alignment)
#Dunno lol
    def generate(self):
        """Empty method that will be called upon at the end of each constructor.
        The idea behind this method is to initiate every element needed for a correct
        Screen usage. Needs to be overloaded on the subclasses that inherit from Screen."""
        pass

#Old dialog
class Dialog (InfoBoard):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text'          : 'dialog',
                        'font'          : None,
                        'max_font_size' : 50,
                        'font_size'     : 0,
                        'text_color'    : WHITE,
                        'auto_center'   : True,
    }

    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, **params):
        for button in buttons:  
            self.buttons.add(button)
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params)
        self.spaces         = 0 #Created in InfoBoard.generate
        self.taken_spaces   = 0

    def add_button(self, size, **button_params):
        pass

    @staticmethod
    def generate(self, rect=None, generate_image=True):
        super().generate(rect=rect, generate_image=False)
        UtilityBox.check_missing_keys_in_dict(self.params, Dialog.__default_config)
        #self.adjust_buttons()
        self.pieces.add(UIElement.close_button(self.get_id()+"_close_exit_button", self.get_event_id(), self.rect))
        self.params['font_size'] = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])//2
        self.add_text(self.params['text'], self.params['font'], self.rect, [x//1.5 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 0)    
        if self.params['auto_center']:  self.rect.topleft = [(x//2-y//2) for x, y in zip(self.get_canvas_size(), self.rect.size)]
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()

   def stop_music(self):   #TODO what to do when playback > than song
        length_played = pygame.mixer.music.get_pos()/1000
        if self.playback+length_played > self.lengths[self.song_index]:
            self.playback = 0
        else:
            self.playback += pygame.mixer.music.get_pos()/1000
        pygame.mixer.music.stop()

#Scren play soudn with force
    def play_sound(self, sound_id):
        for sound in self.sounds.keys():
            if sound_id in sound or sound in sound_id:
                channel = None
                for channel in Screen.SOUND_CHANNELS:
                    if not channel.get_busy():
                        channel.play(self.sounds[sound])
                        return True
                '''if not channel: #Didn't find an empty one, force it
                    Screen.SOUND_CHANNELS[0].play(self.sounds[sound])
                return True'''
        return False

#Game
    def sound_handler(self, command, value):
        #Getting the affected screens:
        sound = True if 'sound' in command else False
        music = True if 'song' in command or 'music' in command else False
        if self.current_screen:
            if 'change' in command:
                if music:
                    if 'menu' in command:
                        for menu in self.get_all_screens('menu'):
                            menu.change_song(value)
                    if 'board' in command:
                        for board in self.get_all_screens('board'):
                            board.change_song(value)
            if 'volume' in command:
                if 'menu' in command:
                    for menu in self.get_all_screens('menu'):
                        menu.set_volume(value, sound, music)
                if 'board' in command:
                    for board in self.get_all_screens('board'):
                        board.set_volume(value, sound, music)

#Game
    def get_all_screens(self, keyword):
        screens = []
        for screen in self.screens:
            if keyword in screen.id:
                screens.append(screen) 
        return screens

#Resizer
    @staticmethod 
    def resize_same_aspect_ratio(element, new_size):
        """Resizes a surface to the closest size achievable to the input
        without changing the original object aspect ratio relation.
        This way the modified object looks way more natural than just a stretched wretch.
        Accepts both pygame.Surface and pygame.sprite.Sprite.
        Args:
            element (:obj: pygame.Surface||pygame.sprite.Sprite):   Element to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (pygame.Surface||:tuple:int):   The resized Surface if the input was a surface.
                                            A tuple of the ratios used to resize if the input was a sprite.
        """
        if isinstance(element, pygame.sprite.Sprite):   return Resizer.__sprite_resize(element, new_size)
        elif isinstance(element, pygame.Surface):       return Resizer.__surface_resize(element, new_size)
        else:                                           BadResizerParamException("Can't resize element of type "+str(type(element)))

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    @staticmethod
    def __surface_resize(surface, new_size):
        """Resizes a surface to the closest size achievable to the input
        without changing the original aspect ratio relation.
        Args:
            surface (:obj: pygame.Surface): Surface to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (pygame.Surface):   The resized Surface."""
        ratio = min([new/old for new, old in zip(new_size, surface.get_size())])
        return pygame.transform.smoothscale(surface, tuple([int(ratio*size) for size in surface.get_size()])) #Resizing the surface
    
    @staticmethod
    def __sprite_resize(sprite, new_size):
        """Resizes a Sprite to the closest size achievable to the input
        without changing the original aspect ratio relation.
        The changes are made in the sprite itself.
        Args:
            sprite (:obj: pygame.sprite.Sprite):    Sprite to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (:tuple:int):   A tuple of the ratios used to resize if the input was a sprite."""
        ratio = min([new/old for new, old in zip(new_size, sprite.rect.size)])
        sprite.rect.size = tuple([int(ratio*size) for size in sprite.rect.size])
        sprite.image = pygame.transform.smoothscale(sprite.image, sprite.rect.size)
        return ratio

#AnimatedSprite
    def check_path(self, surface_path):
        """Check if a id or path has been already loaded.
        Returns:
            (:obj:pygame.sprite.Sprite||boolean):   The sprite associated if sprite_id is found, 
                                                    False otherwise."""
        for i in range(0, len(self.ids)):
            if surface_path == self.surface_paths[i]:    
                return self.original_surfaces[i]
        return False

    def surface_exists(self, sprite_surface):
        """Check if a surface or image has been already loaded.
        Returns:
            (boolean):  True if sprite_surface is already loaded, False otherwise."""
        for i in range(0, len(self.original_surfaces)):
            if sprite_surface == self.original_surfaces[i]:    
                return self.original_surfaces[i]
        return False

#OLD ANIMATION
class Animation(object):
    """Animation class. Inherits from object.
    Its the frame that contains the sprites that make up an entire animation/cutscene.
    Controls the time at which each sprite triggers and ends, and when to stop the animation itself.
    Also has implemented the logic to replay a couple of times, forever or only play 1 time.
    Attributes:
        id(str):
        total_time(float):  Total duration of this animation. In seconds.
        init_time(float):   Initial time at which the animation started. In seconds from the UNIX 0.
        current_time(float):Time that the animation has been playing. In seconds.
        scripted_sprites(:list: ScriptedSprites):
        currently_playing(:list: ScriptedSprites):
        end_event(:obj: pygame.event):  Event that will be sent when the animation ends all of its loops. Notifies the end.
        loops(int): Number of times that the animation will play. If the input argument is 0/negative, it will continue decreasing.
                    No problem, it always compares to zero to end, so with those inputs the animation will play 'forever'.  
        """

    def __init__(self, name, end_event, loops=1):
        """Animation constructor.
        Args:
            name(str):
            end_event(:obj: pygame.event):
            loops(int, default=1):
        """
        self.id                 = name
        self.total_time         = 0
        self.init_time          = 0
        self.current_time       = 0
        self.all_sprites        = []    #To make methods to all the sprites in one line
        self.idle_sprites       = []
        self.playing_sprites    = {}    #Layers will be effective here
        self.done_sprites       = []
        self.end_event          = end_event
        self.loops              = loops

    def set_resolution(self, resolution):
        for sprite in self.all_sprites:
            sprite.set_canvas_size(resolution)

    def add_sprite(self, sprite, init_time, end_time, layer=0):
        """Adds a sprite/component to the animation, with the starting time and 
        the ending time in seconds.
        Args:
            sprite(:obj: ScriptedSprite): Sprite to add.
            init_time(float):   Starting time of the animated sprite.
            end_time(float):    Ending time of the sprite's animation.
            layer(int, default=0):  Layer in which the sprite will be drawn."""
        sprite.init_time = init_time
        sprite.end_time = end_time
        sprite.layer = layer
        self.all_sprites.append(sprite)
        self.idle_sprites.append(sprite)
        self.sort_sprites()
        if end_time > self.total_time:
            self.total_time = end_time

    def set_loops(self, loops):
        """Sets the number of replays of this animation.
        If the input argument is 0 or negative, the animation plays forever.
        Args:
            loops(int): Number of replays for this animation. 0/negative makes it
                        play forever."""
        self.loops = loops

    def end_loop(self):
        """Ends a loop/replay on the animation. Decreases the loops in 1,
        and if after that the loops equal 0, sends the associated end event.
        Restarts the time attributes too."""
        if self.loops >= 0:
            self.loops -= 1
        self.init_time = 0
        self.current_time = 0
        self.restart()
        if self.loops is 0: #Only will end for self.loops over zero.
            event = pygame.event.Event(self.end_event, command=self.id+"_end_animation")
            pygame.event.post(event)

    def sort_sprites(self, idle=True, playing=False):
        """sorts by init time or end itme, the idle sprites and the playing sprites."""
        if idle:
            self.idle_sprites.sort(key=lambda spr: spr.init_time)
        if playing:
            for layer in self.playing_sprites.keys():
                self.playing_sprites[layer].sort(key=lambda sprite: sprite.end_time)
                #This line is to use to sort by two parameters
                #self.playing_sprites.sort(key=lambda sprite: (sprite.layer, sprite.end_time))

    def restart(self):  #TODO CHECK OUT THIS METHOD
        for sprite in self.playing_sprites:
            sprite.restart()
            self.idle_sprites.append(sprite)
        for sprite in self.done_sprites:
            self.idle_sprites.append(sprite)
        self.clear_animation_cache()
        self.sort_sprites()

    def clear_animation_cache(self):
        for layer in self.playing_sprites.keys():
            del self.playing_sprites[layer][:]
        del self.done_sprites[:]

    def play(self, surface, infinite=False):
        """Plays the animation. Draws a frame of it and updates the attributes to
        continue the animation the next time this method is called.
        Args:
            (:obj: pygame.Surface): Surface to draw the animation frame on."""
        self.update_clocks()
        self.trigger_sprites()
        if not infinite and (self.current_time > self.total_time):
            self.end_loop()
        else:
            for layer in self.playing_sprites.keys():
                for sprite in self.playing_sprites[layer]:
                    sprite.draw(surface)

    def draw(self, surface):
        """Acronym"""
        self.play(surface)

    def update_clocks(self):
        """Updates the time attributes. Called along with the play() method."""
        time_now = time.time()
        if self.init_time is 0: #First time playing this loop
            self.init_time = time_now
        self.current_time = time_now-self.init_time

    def trigger_sprites(self):
        #Checking sprites that have completed their animation to end them.
        for layer in self.playing_sprites.keys():
            indexes_to_end = []
            for index in range (0, len(self.playing_sprites[layer])): #They are sorted, if the first one is not a hit, no need to keep checking.
                if self.current_time > self.playing_sprites[0].end_time:
                    indexes_to_end.append(index)
                    continue
                self.end_sprites(layer, *indexes_to_end)
                break
        #Checking sprites to trigger/start. They are sorted, sooo...
        indexes_to_start = []
        for index in range (0, len(self.idle_sprites)):
            #print("NOT TRUE "+str(self.current_time) +" NOT GREATER THAN "+str(self.idle_sprites[index].init_time))
            if self.current_time > self.idle_sprites[index].init_time:
                indexes_to_start.append(index)
                continue    #Next iteration
            self.init_sprites(*indexes_to_start)
            break

    def init_sprites(self, *indexes):
        offset = 0
        for index in indexes:
            sprite = self.idle_sprites[index]
            layer = sprite.layer
            try:
                self.playing_sprites[layer].append(sprite)
            except KeyError:
                self.playing_sprites[layer] = [sprite]
                self.playing_sprites = sorted(self.playing_sprites.items())
            del self.idle_sprites[index-offset]
            offset+=1
        self.sort_sprites(idle=True, playing=True)

    def end_sprites(self, layer, *indexes):
        offset = 0
        for index in indexes:
            sprite = self.playing_sprites[layer][index]
            sprite.restart()
            self.done_sprites.append(sprite)
            del self.playing_sprites[layer][index-offset]
            offset+=1

    def set_fps(self, fps):
        """Sets the refresh rate of the animation.
        Args:
            fps(int):   Frames per second to set as refresh rate."""
        for sprite in self.all_sprites:
            sprite.set_refresh_rate(fps)
    
    def speedup(self, ratio):
        """Speeds up the animation by increasing the frame jump attribute.
        If wanted to speed down, a number between 0 and 1 must be used.
        Args:
            ratio(int|float):   The factor to speed up the animation.
                                e.g: A ratio 2 makes the animation go double the speed.
                                ratio 0.5 makes it go half the speed."""
        ratio = int(ratio)
        for sprite in self.all_sprites:
            sprite.time /= ratio
            sprite.frame_jump *= ratio

    def set_speed(self, speed):
        """Sets the speed of the animation by setting the frame jump attribute and time.
        A speed of 1 is the default speedof the animation.
        Args:
            ratio(int|float):   The factor to speed up the animation.
                                e.g: A ratio 2 makes the animation go double the speed."""
        speed = int(speed)
        for sprite in self.all_sprites:
            sprite.time /= (speed/sprite.frame_jump)
            sprite.frame_jump = speed    

    def shrink_time(self, ratio):
        """Divides the time of the animation by the ratio, getting a shorter animation by a factor of x
        Deletes frames in the process, irreversible method. This leads to a speed up animation.
        Args:
            ratio(int|float):   The factor to shrink the frames lists.
                                e.g: A ratio 2 deletes half the sprites, thus making the animation
                                half the duration.
                                A ratio 3 deletes 2/3 the sprites, thus making the animation one third
                                the duration."""
        ratio = int(ratio)
        for sprite in self.all_sprites:
            sprite.index //= ratio
            sprite.time /= ratio
            for key in sprite.frames.keys():
                new_frame_list = []
                for i in range(0, len(sprite.frames[key])):
                    if i%ratio != 0:
                        new_frame_list.append(sprite.frames[key][i])
                sprite.frames[key] = new_frame_list

class LoopedAnimation(Animation):
    """LoopedAnimation class. Inherits from Animation.
    The sprites in this animation will loop back as soon as they are done.
    In this way specific sprites can be restarted before than others.
    Has no loops funcionality, plays forever.
    All the sprites are called from the get-go, no triggering based in time.
    It's like a basic and lite version of Animation, perfect for menu animations and such.
    If you want an infinite animation, but with different trigger times for sprites, use Animation
    with loops set to 0 or a negative number.
    """
    def __init__(self, name, loops=1):
        super().__init__(name, -1, -1)

    def trigger_sprites(self):
        #Checking sprites to trigger/start. They are sorted, sooo...
        indexes_to_start = []
        for index in range (0, len(self.idle_sprites)):
            if self.current_time > self.idle_sprites[index].init_time:
                indexes_to_start.append(index)
                continue    #Next iteration
            self.init_sprites(*indexes_to_start)
            break

    def play(self, surface):
        """Plays the animation. Draws a frame of it and updates the attributes to
        continue the animation the next time this method is called.
        Args:
            (:obj: pygame.Surface): Surface to draw the animation frame on."""
        super().play(surface, infinite=True)