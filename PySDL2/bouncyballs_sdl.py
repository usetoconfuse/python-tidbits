import sys
import math
import sdl2
import sdl2.ext
import sdl2.sdlimage
import sdl2.sdlttf

sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG)
sdl2.sdlttf.TTF_Init()

BROWN = sdl2.ext.Color(50,10,0)
WHITE = sdl2.SDL_Color(255,255,255)
BLACK = sdl2.SDL_Color(0,0,0)

RESOURCES = sdl2.ext.Resources(__file__, "bouncyballs_gfx")

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super().__init__()
        self.componenttypes = Physics, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
    
    def process(self, world, componentsets):
        for physics, sprite in componentsets:
            swidth, sheight = sprite.size
            if physics.accy:
                physics.vy += 0.2
            if physics.accx:
                if physics.vx < 0:
                    physics.vx += 0.05
                elif physics.vx > 0:
                    physics.vx -= 0.05
            sprite.x += round(physics.vx)
            sprite.y += round(physics.vy)

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            framemaxx = sprite.x+swidth
            framemaxy = sprite.y+sheight

            if framemaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if framemaxy > self.maxy:
                sprite.y = self.maxy - sheight

class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = Physics, sdl2.ext.sprite
        self.boxes = None

    def overlap(self, sprite1, sprite2):
        dx = sprite2.x - sprite1.x
        dy = sprite1.y - sprite2.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= 30:
            return dx, dy
        else:
            return 5000, 5000

    def process(self, world, componentsets):
        for i in range (0, len(self.boxes)):
            box = self.boxes[i]
            if box.sprite.y >= 820:
                box.physics.vy = 0
                box.sprite.y = 820
            if box.sprite.x == 0 or box.sprite.x == 1170:
                box.physics.vx *= -1
            for j in range (i + 1, len(self.boxes)):
                box2 = self.boxes[j]
                dx, dy = self.overlap(box.sprite, box2.sprite)
                if (dx, dy) != (5000, 5000):
                    if box.sprite.y < 820:
                        box.physics.vy = 0.15 / box.physics.m * (box2.physics.vy+dy)
                    if box2.sprite.y < 820:
                        box2.physics.vy = -0.15 / box.physics.m * (box.physics.vy+dy)
                    box.physics.vx = -0.15 / box.physics.m * (box2.physics.vx+dx)
                    box2.physics.vx = 0.15 / box.physics.m * (box.physics.vx+dx)

class SpriteRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SpriteRenderer, self).__init__(window)
    def render(self, components):
        sdl2.ext.fill(self.surface, BLACK)
        super(SpriteRenderer, self).render(components)

class Physics(object):
    def __init__(self, vx=0, vy=0, m=1):
        super().__init__()
        self.vx = vx
        self.vy = vy
        self.m = m
        self.accy = True
        self.accx = False

class Box(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy, mm):
        super().__init__()
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.physics = Physics(m=mm)

class Floor(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy):
        super().__init__()
        self.sprite = sprite
        self.sprite.position = posx, posy

class Counter(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy):
        super().__init__()
        self.sprite = sprite
        self.sprite.position = posx, posy
    
    def update(self, sprite):
        posx, posy = self.sprite.position
        self.sprite = sprite
        self.sprite.position = posx, posy

def getFPS(frames, pframes, deltatime):
    deltaframes = frames - pframes
    fps = math.trunc(deltaframes / deltatime)
    if fps > 2000000:
        fps = 0
    return fps

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("epic physics",size=(1200,900))
    window.show()

    world = sdl2.ext.World()

    collsys = CollisionSystem()
    movementsys = MovementSystem(0,0,1200,900)
    softrenderer = SpriteRenderer(window)

    world.add_system(collsys)
    world.add_system(movementsys)
    world.add_system(softrenderer)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sp_floor = factory.from_color(BROWN,size=(1200,50))
    floor = Floor(world, sp_floor, 0, 850)
    collsys.floor = floor
    boxes = []
    collsys.boxes = boxes

    arialpath = RESOURCES.get_path("arial.ttf").encode()
    arial = sdl2.sdlttf.TTF_OpenFont(arialpath, 40)

    bcount = 0
    sp_bcounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, "0".encode(), WHITE))
    bcounter = Counter(world, sp_bcounter, 1050, 50)

    frames = 0
    pframes = 0
    ptime = 0
    sp_bcounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, "0".encode(), WHITE))
    fpscounter = Counter(world, sp_bcounter, 0, 0)

    ballfile = RESOURCES.get_path("ball1.png")
    mcurrent = 1
    sp_mcounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, "1".encode(), WHITE))
    masscounter = Counter(world, sp_mcounter, 150, 50)

    running = True
    while running:
        events = sdl2.ext.get_events() 
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                if event.button.button == sdl2.SDL_BUTTON_LEFT:
                    sp_box = factory.from_image(ballfile)
                    boxes.append(Box(world, sp_box, event.button.x-15, event.button.y-15, mcurrent))
                    bcount += 1
                    sp_bcounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, str(bcount).encode(), WHITE))
                    bcounter.update(sp_bcounter)
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_1:
                    mcurrent = 1
                    ballfile = RESOURCES.get_path("ball1.png")
                elif event.key.keysym.sym == sdl2.SDLK_2:
                    mcurrent = 2
                    ballfile = RESOURCES.get_path("ball2.png")
                elif event.key.keysym.sym == sdl2.SDLK_3:
                    mcurrent = 3
                    ballfile = RESOURCES.get_path("ball3.png")
                elif event.key.keysym.sym == sdl2.SDLK_4:
                    mcurrent = 4
                    ballfile = RESOURCES.get_path("ball4.png")
                elif event.key.keysym.sym == sdl2.SDLK_5:
                    mcurrent = 5
                    ballfile = RESOURCES.get_path("ball5.png")
                sp_mcounter = sp_mcounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, str(mcurrent).encode(), WHITE))
                masscounter.update(sp_mcounter)
        sdl2.SDL_Delay(17)
        frames += 1
        time = sdl2.SDL_GetTicks() / 1000
        deltatime = time - ptime
        if deltatime > 1:
            fps = getFPS(frames, pframes, deltatime)
            pframes = frames
            ptime = time
            strfps = str(fps).encode()
            sp_fpscounter = factory.from_surface(sdl2.sdlttf.TTF_RenderUTF8_Solid(arial, strfps, WHITE))
            fpscounter.update(sp_fpscounter)
        world.process()
    
if __name__ == "__main__":
    sys.exit(run())