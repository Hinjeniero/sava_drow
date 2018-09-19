import numpy, math, time, pygame, gradients, random

class UtilityBox (object):
    size = (2,2)
    mouse_sprite = pygame.sprite.Sprite()
    mouse_sprite.image = pygame.Surface(size)       #Creating surface of mouse sprite
    mouse_sprite.image.fill((0, 0, 0))              #Filling surface with BLACK solid color
    mouse_sprite.rect = pygame.Rect((0,0), size)    #Decoy sprite to check collision with mouse
    mouse_sprite.mask = pygame.mask.Mask(size)      #Creating the mask to check collisions with masks
    mouse_sprite.mask.fill()                        #Filling it with ones

    @staticmethod
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

    @staticmethod
    def draw_hitbox(surface, sprite, color=(255, 0, 0)):
        pygame.draw.rect(surface, color, sprite.rect, 2)

    @staticmethod
    def load_background(size, background_path=None):
        if background_path is None:
            bg_surf = gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) #Gradient from white-ish to red
        else:
            bg_surf = pygame.transform.scale(pygame.image.load(background_path), size)
        return bg_surf

    @staticmethod
    def get_mouse_sprite(mouse_position):
        UtilityBox.mouse_sprite.rect.topleft = mouse_position
        return UtilityBox.mouse_sprite

    @staticmethod
    def random_rgb_color(start=0, end=255):
        return (random.randint(start, end), random.randint(start, end), random.randint(start, end))
