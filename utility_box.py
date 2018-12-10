import numpy, math, time, pygame, gradients, random 

def euclidean_generator(dimension=300, print_time=False): #100 will be plenty in our case
    start = time.time()
    matrix = numpy.empty([dimension+1, dimension+1])
    x = 0
    for i in range (0, dimension+1):
        for j in range (x, dimension+1):
            euclidean = math.sqrt(i*i + j*j)
            matrix[i][j] = euclidean
            matrix[j][i] = euclidean
        x+=1
    if print_time:  print ("Total time: "+str(time.time()-start)+" seconds") #TODO search a better one-liner for this
    return matrix

class UtilityBox (object):
    size = (2,2)
    mouse_sprite = pygame.sprite.Sprite()
    mouse_sprite.image = pygame.Surface(size)       #Creating surface of mouse sprite
    mouse_sprite.image.fill((0, 0, 0))              #Filling surface with BLACK solid color
    mouse_sprite.rect = pygame.Rect((0,0), size)    #Decoy sprite to check collision with mouse
    mouse_sprite.mask = pygame.mask.Mask(size)      #Creating the mask to check collisions with masks
    mouse_sprite.mask.fill()                        #Filling it with ones
    EUCLIDEAN_DISTANCES = euclidean_generator(print_time=True)

    @staticmethod
    def draw_hitboxes(surface, *sprites, color=(255, 0, 0)):
        if isinstance(sprites, list, tuple): 
            for sprite in sprites: 
                UtilityBox.draw_hitbox(surface, sprite, color)
        else:   raise AttributeError("Bad *sprites attribute in UtilityBox")

    @staticmethod
    def draw_hitbox(surface, sprite, color=(255, 0, 0)):
        pygame.draw.rect(surface, color, sprite.rect, 2)

    @staticmethod
    def load_background(size, background_path=None, fill=True, centered=False):
        if background_path is None: return gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) #Gradient from white-ish to red
        if not fill:                return pygame.transform.smoothscale(pygame.image.load(background_path), size)
        return UtilityBox.fill_surface(size, background_path, centered)

    @staticmethod
    def fill_surface(size, source_surf, centered=False):
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
    def get_mouse_sprite(mouse_position):
        UtilityBox.mouse_sprite.rect.topleft = mouse_position
        return UtilityBox.mouse_sprite

    @staticmethod
    def random_rgb_color(start=0, end=255):
        return (random.randint(start, end), random.randint(start, end), random.randint(start, end))

    @staticmethod
    def draw_fps(surface, clock):
        fnt = pygame.font.Font(None, 60)
        frames = fnt.render(str(int(clock.get_fps())), True, pygame.Color('white'))
        surface.blit(frames, (50, 150))

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

    @staticmethod
    def check_missing_keys_in_dict(dict_to_add_keys, dict_to_search_keys):
        for key in dict_to_search_keys.keys(): 
            key = key.lower().replace(" ", "_")
            if key not in dict_to_add_keys: dict_to_add_keys[key] = dict_to_search_keys[key]

    @staticmethod
    def rotate(sprite, angle, iterations, offset=0, include_original=False): #TODO BE CAREFUL WITH THE REFERENCES, DUNNO IF THE LIST OF SPRITES ARE DIFFERENT SPRITERS!
        #TODO implement difference between sprite and surface, to make it a valid method for both
        sprites         = [sprite] 
        orig_surface    = sprite.image
        orig_rect       = sprite.rect
        curr_angle      = angle+offset
        for _ in range (0, iterations):
            surf = pygame.transform.rotate(orig_surface, curr_angle)
            rect = surf.get_rect()
            rect.center = orig_rect.center
            sprite = pygame.sprite.Sprite()
            sprite.image, sprite.rect = surf, rect
            sprites.append(sprite)
            curr_angle += angle
        return sprites[1:] if not include_original else sprites

    @staticmethod
    def draw_grid(surface, rows, columns, color=(255, 0, 0)):
        for i in range(0, surface.get_height(), surface.get_height()//rows):    pygame.draw.line(surface, color, (0, i), (surface.get_width(), i))
        for i in range(0, surface.get_width(), surface.get_width()//columns):   pygame.draw.line(surface, color, (i, 0), (i, surface.get_height()))

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
