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