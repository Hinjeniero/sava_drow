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