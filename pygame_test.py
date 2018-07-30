import pygame, time

class Pygame_suite:
    def __init__(self, resolution=(1280, 720), background=(0,0,0), fps=60, mouse=True):
        self.background = background
        self.fps = fps
        self.clock, self.screen = self.initiate_suite(resolution, background, fps, mouse)
        self.elements = [] #Tuples of (surface, rect)

    def initiate_suite(self, resolution=(1280, 720), background=(0,0,0), fps=60, mouse=True):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mouse.set_visible(True)
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(resolution)
        return clock, screen
    
    def add_element(self, element_surf, element_rect):
        self.elements.append((element_surf, element_rect))

    def draw(self, surface, element_to_draw, element_rect):
        surface.blit(element_to_draw, element_rect)

    def loop(self, seconds=5, show_fps=True):
        start = time.time()
        loop = True
        while loop:
            self.clock.tick(self.fps)
            if (time.time()-start) > seconds:
                break
            self.screen.fill(self.background) #Drawing mackground
            for element in self.elements: #Drawing test elements
                self.draw(self.screen, element[0], element[1])
            if show_fps: #Showing fps in screen
                fnt = pygame.font.Font(None, 60)
                frames = fnt.render(str(int(self.clock.get_fps())), True, pygame.Color('white'))
                self.screen.blit(frames, (50, 150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        loop = False
            pygame.display.update() #Updating the screen
    