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