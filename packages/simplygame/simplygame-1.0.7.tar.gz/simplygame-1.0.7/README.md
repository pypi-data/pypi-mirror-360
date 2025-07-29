# ⭐ Simply Game
[![PyPI Downloads](https://static.pepy.tech/badge/simplygame)](https://pepy.tech/projects/simplygame)

**A module to create games and animations more easily**

## 🚀 Try
- https://pypi.org/project/simplygame/


##  🛬 Download
First time:
```bash
pip install simplygame
```

To update:
```bash
pip install simplygame --upgrade
```

To import:
```python
import simplygame as SG
```

## 🤖 Features
🚨The project is currently under construction, some features may not work. New features will also be coming🚨

### Create a window
The first step in creating a project is to create a window. To do this, simply give it a name and size.
```python
SG.create_window("title", 800, 600)
```
⚠️ **You'll notice that the window will close instantly.**
**To avoid this problem, you need to define a variable that keeps the window open.**
**However, simply doing this will cause the program to crash. To do this, you need to tell it to wait for an event, usually the 'exit' event.**

```python
#define a running variable
running = True

SG.create_window("title", 800, 600) #Create a window

while running:
    event = SG.recover_event() #Save event into 'event' variable
    if event == 'exit':
        running = False #And close while loop
```

### Load image into memory
Store image into a variable
```python
SG.load_image(path)
```

For example:
```python
img = SG.load_image('example.png')
```
Now, 'example.png' is stored in memory and accessible with the variable 'img'

### Events
Several events are possible to be recovered:
- 'exit' : If user wants to close the program
- 'pressed': If user press a key
- 'released': If user release a key
- 'mouse_motion': If user move the mouse

First Step: Create a variable to store the event
```python
event = SG.recover_event() #This function return the events mentioned before
```
⚠️ **To work, it must be done in the loop 'running'**

➡️*Example: We want to know if a key is pressed. If so, we print 'hello world'*
```python
running = True

SG.create_window("title", 800, 600) 

while running:
    event = SG.recover_event() #Save event into 'event' variable
    if event == 'exit':
        running = False
    elif event == 'pressed':
        print('hello world')
```

### Key
Return pressed or released key

```python
SG.recover_key()
```

### Mouse position
Returns the mouse position

```python
SG.mouse_position()
```

Return mouse's x position only:
```python
SG.mouse_x()
```

Return mouse's y position only:
```python
SG.mouse_y()
```

### Update
🚨It is mandatory for a project to have this at the end of its loop, otherwise nothing will happen on screen when you add objects
```python
SG.update()
```

### Reset window
Useful to return to the 'default' window
```python
SG.reset_window()
```

### Change background color
Allows you to enter an RGB value to define a new screen color

```python
SG.window_fill((255,192,203)) #Have a pink window
```
⚠️ **It is better to create a variable to avoid parentheses problems:**
```python
PINK = (255,192,203) #Declare a variable with color
SG.window_fill(PINK) #Use variable to have a pink window
```

### FPS
Change the project's FPS
🚨We recommend applying '60'

```python
SG.tick(60)
```

### Draw a rectangle
To draw a rectangle, you need to know the x,y position of the top-left point.
You then need to specify its length, then its width. Finally, give it a color.

**Use:**
```python
SG.draw_rect(x,y,width,height,color)
```

➡️*Example: We want a square that is 50px by 50px. Blue in color.*
```python
BLUE = (0,0,255)
SG.draw_rect(0,0,50,50,BLUE)
```

### Draw a circle
To draw a circle, you need the x,y position of its center, its radius and its color

**Use:**
```python
SG.draw_circle(x,y,radius,color)
```

➡️*Example: We want a 100px by 100px circle in the middle of the screen. It's red.*
```python
RED = (255,0,0)
SG.draw_circle(400,300,100,RED)
```

### Draw a pixel
To draw a circle, you need the x,y position of its center, its radius and its color

```python
SG.draw_pixel(x,y,color)
```

### Draw a image
To draw a image in the same folder of the current file, after import it

```python
SG.draw_image(img, x, y, transparency)
```
🚨Transparency = 255 by default