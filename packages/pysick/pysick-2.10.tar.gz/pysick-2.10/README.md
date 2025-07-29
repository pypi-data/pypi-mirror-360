# PySick 
**_An Bypass for learning Graphics Development_ made using Tkinter, designed for simplicity and customization.**
## Features 
- **Window Management**
  - Set custom window size and title.
  - Change background color dynamically.

- **Shapes & Drawing**
  - Draw rectangles, circles, ovals, and lines with customizable colors.
  - Fill the screen with a solid color.

- **Collision Detection**
  - Rectangle vs. rectangle (AABB method).
  - Circle vs. circle (distance-based).
  - Circle vs. rectangle (bounding box method).

- **Event Handling**
  - Bind keys dynamically for interaction (`lock()` and `unlock()` methods).
  - Support for real-time keyboard inputs.

- **UI Elements**
  - Add **labels** with customizable font and color.`
  - Create **buttons** with event-driven functionality.

## EXAMPLE PROGRAM
```python 
import pysick
game = pysick.pysick_.InGine(1200, 700)
pysick.graphics.fill_screen(game, 'yellow')

playerx = 0
playery = 0
speed = 10

def left():
    global playerx
    playerx -= speed

def right():
    global playerx
    playerx += speed

def up():
    global playery
    playery -= speed

def down():
    global playery
    playery += speed

game.lock('<Left>', left)
game.lock('<Right>', right)
game.lock('<Up>', up)
game.lock('<Down>', down)

def update():
    pysick.graphics.fill_screen(game,'violet')  # Clear screen
    pysick.graphics.draw_rect(game,playerx, playery, 100, 100, fill='white')  # Correct rect drawing
    game.time_in(16, update)  # Call update again in ~16ms (~60 FPS)

update()
game.sickloop()
```
## **MESSAGE BOX**
+ SYNTAX:
 ```bash
pysick_.{your_need}(title, text)
```
- pysick_.*ask_question*
- pysick_.*show_info*
- pysick_.*show_warning*
- pysick_.*show_error*
- pysick_.*about*
## Installation 
Install PySick using:
```bash
pip install PySick
```
## NOTE

- This module uses FFmpeg for video processing.

+ FFmpeg is licensed under the GNU General Public License (GPL) or 
the Lesser GPL (LGPL) depending on configuration. See https://ffmpeg.org for details.

- FFmpeg Copyright (c) 2000-2024 the FFmpeg developers

thanks to - FFmpeg,
		   Tkinter for playing an important role in formation of this module.