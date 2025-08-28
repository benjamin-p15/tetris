import pygame
import random
import copy

score=0

positionX = 0
positionY = 0
interval=500
move_delay=100
scale=32

filled_peices_array=False
peices = {}

class grid:
    def __init__(self,screen):
        self.screen=screen
    def place_image(self,imagePath,x,y):
        image = pygame.image.load(imagePath)
        image=pygame.transform.scale(image, (scale,scale))
        self.screen.blit(image, (x, y))
    def place_shape(self,shape,shapeColor, x=None, y=None):
        offset_x = x if x is not None else positionX  
        offset_y = y if y is not None else positionY
        for block in shape:
            self.place_image(shapeColor,block[0]*scale+offset_x,block[1]*scale+offset_y)
    def background(self,x,y):
        for countX in range(x):
            for countY in range(y):
                self.place_image("background.png",countX*scale,countY*scale)
                global filled_peices_array
                global peices
                if filled_peices_array == False:
                    peices[f"{countX}_{countY}"]=0
                peice=peices[f"{countX}_{countY}"]
                if peice !=0: 
                    self.place_image(peice,countX*scale,countY*scale)
        filled_peices_array=True           
    def keyMoves(self,pygame,shape):
        global positionX
        global positionY
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.moveCheck(shape,"right"):positionX -= scale

        if keys[pygame.K_RIGHT]:
            if self.moveCheck(shape,"left"):positionX += scale

        if keys[pygame.K_DOWN]:
            self.moveDown(shape)
    def events(self,event,pygame,shape):
        global positionX
        global positionY
        global last_move_time
        global shape_name
        global held
        global held_shape
        global current_shape
        global next_shapes_queue
        global shapes
        global colors
        global current_color
        global positionX
        global width
        if event.type == pygame.QUIT:
            pygame.quit()
        if endGame == True: return
        if event.type == pygame.KEYDOWN:
            last_move_time = current_time
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.moveCheck(shape,"right"):positionX -= scale
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.moveCheck(shape,"left"):positionX += scale
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.moveDown(shape)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if shape_pivot[shape_name] is False: return
                px, py = shape[shape_pivot[shape_name]]
                new_shape=[]
                for i in range(len(shape)):
                    x, y = shape[i]
                    tx = x - px
                    ty = y - py   
                    rx = -ty 
                    ry = tx
                    new_shape.append([rx + px, ry + py])
                if self.rotate_check(new_shape) == False: return
                shape[:]=new_shape 
            elif event.key == pygame.K_SPACE:
                while True:
                    if self.moveDown(shape) is False: break
            elif event.key == pygame.K_c:
                if held == True: return
                held = True
                positionY=scale
                if held_shape is None:
                    held_shape = (shape_name, copy.deepcopy(current_shape), current_color)
                    shape_name, current_shape, current_color = next_shapes_queue.pop(0)
                    current_shape = copy.deepcopy(current_shape)
                    new_name, new_coords = random.choice(list(shapes.items()))
                    new_color = colors[new_name]
                    next_shapes_queue.append((new_name, copy.deepcopy(new_coords), new_color))
                    self.reposition(current_shape)
                else:
                    held_shape2 = (shape_name, copy.deepcopy(current_shape), current_color)
                    shape_name, current_shape, current_color = held_shape
                    held_shape=held_shape2
                    self.reposition(current_shape)
    def moveDown(self,shape):
        if self.moveCheck(shape,"none") == False:
            return False
        global positionY
        positionY+=scale
    def reposition(self, shape):
        global positionX
        shape_coords = shape
        left_bound = 0
        right_bound = width  
        block_size = scale   
        while True:
            out_of_bounds = False
            for x, y in shape_coords:
                block_x = int(positionX / block_size) + x
                if block_x < left_bound:
                    positionX += block_size
                    out_of_bounds = True
                    break
                elif block_x >= right_bound // block_size:
                    positionX -= block_size
                    out_of_bounds = True
                    break
            if not out_of_bounds:
                break
    def moveCheck(self,shape,exclude):
        checks=[]
        if exclude=="left":checks=[[1,0],[0,-1]]
        elif exclude=="right":checks=[[-1,0],[0,-1]]
        else: checks=[[0,1]]
        for peice in shape:
            locX=int(positionX / scale)+peice[0]
            locY=int(positionY / scale)+peice[1]
            for check in checks:
                key = f"{locX+check[0]}_{locY+check[1]}"
                if key not in peices or peices[key] != 0:
                    if exclude=="none": self.place_position_part(shape)
                    return False
        return True
    def place_position_part(self,shape):
        global peices
        global positionX
        global positionY
        global current_shape
        global current_color
        global shape_name
        global held 
        for i, peice in enumerate(shape):
            locX=int(positionX / scale)+peice[0]
            locY=int(positionY / scale)+peice[1]
            peices[f"{locX}_{locY}"]=colors[shape_name]
            if i == len(shape) - 1: 
                positionX = width/2
                positionY = 0
                held = False
                self.clearRows()

                shape_name, current_shape, current_color = next_shapes_queue.pop(0)
                current_shape = copy.deepcopy(current_shape)

                new_name, new_coords = random.choice(list(shapes.items()))
                new_color = colors[new_name]
                next_shapes_queue.append((new_name, copy.deepcopy(new_coords), new_color))
                
                return False
            else: continue
    def rotate_check(self,shape):
        for peice in shape:
            locX=int(positionX / scale)+peice[0]
            locY=int(positionY / scale)+peice[1]
            key = f"{locX}_{locY}"
            if key not in peices or peices[key] != 0: return False
        return True
    def clearRows(self):
        global score
        xBlocks = int(size/scale)
        yBlocks = int(size*2/scale)
        y = yBlocks - 1
        while y >= 0:
            full_row = True
            for x in range(xBlocks):
                key = f"{x}_{y}"
                if key not in peices or peices[key] == 0: 
                    full_row = False
                    break
            if full_row == True:
                for x in range(xBlocks):
                    key = f"{x}_{y}"
                    if key in peices: 
                        peices[key]=0
                        score+=1
                for currentY in range(y-1, -1, -1):
                    for x in range(xBlocks):
                        oldKey = f"{x}_{currentY}"
                        newKey = f"{x}_{currentY+1}"
                        peices[newKey] = peices.get(oldKey, 0)
            else: y-=1
    def detectEndGame(self):
        global endGame
        xBlocks = int(size/scale)
        for y in range(2):
            for x in range(xBlocks):
                key = f"{x}_{y}"
                if key in peices:
                    if peices[key] != 0: 
                        endGame = True
                        return
        return

#color,xStart,yStart
colors = {
    "I": "cyan_cube.png",
    "O": "yellow_cube.png",
    "T": "purple_cube.png",
    "S": "green_cube.png",
    "Z": "red_cube.png",
    "J": "blue_cube.png",
    "L": "orange_cube.png",
}

shapes = {
    "I": [[0,0],[1,0],[2,0],[3,0]],
    "O": [[0,0],[1,0],[1,1],[0,1]],
    "T": [[0,0],[1,0],[2,0],[1,1]],
    "S": [[1,0],[2,0],[0,1],[1,1]],
    "Z": [[0,0],[1,0],[1,1],[2,1]],
    "J": [[0,0],[0,1],[1,1],[2,1]],
    "L": [[2,0],[0,1],[1,1],[2,1]],
}
shape_pivot = {
    "I": 1,
    "O": False,  
    "T": 1,  
    "S": 0,  
    "Z": 2,  
    "J": 2, 
    "L": 2
}

shape_name, current_shape = random.choice(list(shapes.items()))
current_color = colors[shape_name]
current_shape = copy.deepcopy(current_shape)
next_shapes_queue = []
held_shape=None
for _ in range(3):
    name, shape = random.choice(list(shapes.items()))
    color = colors[name]
    next_shapes_queue.append((name, copy.deepcopy(shape), color))

pygame.init()
size=400
ui=200

held = False
font = pygame.font.Font(None, 36)
fontHuge = pygame.font.Font(None, 96)
width = size
height=size*2
screen = pygame.display.set_mode((width+ui, height))
overlay = pygame.Surface((width+ui, height), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 192))
positionX = width/2
scale=height/20
positionY=scale
clock = pygame.time.Clock()
grid=grid(screen)
running = True
last_run = 0
last_move_time = 0
endGame=False
shapeColor="purple_cube.png"

while running:
    if endGame == False: grid.detectEndGame()

    screen.fill((28,25,33))
    current_time = pygame.time.get_ticks() 
    for event in pygame.event.get(): grid.events(event,pygame,current_shape)
    if current_time - last_move_time > move_delay: 
        grid.keyMoves(pygame,current_shape)
        last_move_time = current_time
    grid.background(10,20)

    text = font.render(f"Next:", True, (255, 255, 255)) 
    screen.blit(text, (width+10,height/6-scale))
    for i, (name, shape, color) in enumerate(next_shapes_queue):
        x_offset = width + 10
        y_offset = int(height/6) + i * (scale*3.75)  
        grid.place_shape(shape, color, x_offset, y_offset)

    text = font.render(f"Hold:", True, (255, 255, 255)) 
    screen.blit(text, (width+10,height/1.25-scale*2))

    if held_shape is not None:
        held_shape_name, held_current_shape, held_current_color = held_shape
        x_offset = width + 10
        y_offset = int(height/1.4) + i * (scale*1)  
        grid.place_shape(held_current_shape, held_current_color, x_offset, y_offset)


    shapeColor = colors[shape_name]
    if endGame == False: grid.place_shape(current_shape,shapeColor)
    text = font.render(f"score: {score}", True, (255, 255, 255)) 
    screen.blit(text, (width+10, 10))
    if current_time - last_run > interval:
        last_run = current_time
        if endGame == False: grid.moveDown(current_shape)
    if endGame == True:
        screen.blit(overlay, (0, 0))
        text = fontHuge.render(f"score: {score}", True, (255, 255, 255)) 
        screen.blit(text, (int(width/2-32),int(height/4)))
    clock.tick(60)  # limits FPS to 60
    pygame.display.flip()
pygame.quit()