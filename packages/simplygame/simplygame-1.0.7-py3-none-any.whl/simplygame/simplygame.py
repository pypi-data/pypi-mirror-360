"""
Created 01/07/2025 (FR) | 07/01/2025 (EN)
"""
__version__ = "1.0.7"
import pygame
from pygame import *
pygame.init()

window = None
running = False
clock = pygame.time.Clock()
def create_window(windowName, width, height):
    """Create a window"""
    global window, running, clavier
    clavier = {}
    window = pygame.display.set_mode([width, height])
    pygame.display.set_caption(windowName)
    window.fill((255, 255, 255))
    update()


def update():
    """Update window's objects"""
    pygame.display.flip()

def reset_window():
    """Return as a default stat, with default background color"""
    window.fill((255, 255, 255))

def window_fill(color):
    window.fill(color)


def tick(fps):
    """Limit frame rate"""
    clock.tick(fps)

def get_version():
    """Return current version of simplygame"""
    return __version__

##Draw
def draw_rect(x,y,width,height,color):
    """Draw a rectangle"""
    pygame.draw.rect(window, color, (x,y,width,height))

def draw_circle(x,y,radius,color):
    """Draw a circle"""
    pygame.draw.circle(window, color, (x,y), radius)

def draw_pixel(x,y,color):
    """Draw a pixel"""
    pygame.draw.rect(window, color, (x,y,1,1))


##Events
def recover_event():
    global event
    """
    Allows you to retrieve events
    Events:
    - exit
    - pressed
    - released
    """
    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        running = False
        return "exit"
    
    elif event.type == pygame.KEYDOWN:
        return 'pressed'
    
    elif event.type == pygame.KEYUP:
        return 'released'
    
    elif event.type == pygame.MOUSEMOTION:
        return 'mouse_motion'

    return None

def recover_key():
    """Return character was pressed"""
    global event
    character = pygame.key.name(event.key)
    return character


def mouse_x():
    global event
    """Return mouse's x position"""
    return event.pos[0]

def mouse_y():
    global event
    """Return mouse's y position"""
    return event.pos[1]

def mouse_position():
    """Return mouse's position"""
    return mouse_x(), mouse_y()

def load_image(path):
    if pygame.display.get_init==True:
        return pygame.image.load(path).convert_alpha()
    else:
        return pygame.image.load(path)
    
def draw_image(img, x, y, transparency):
    if transparency == 255:
        window.blit(img,(x,y))