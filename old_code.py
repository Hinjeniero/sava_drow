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