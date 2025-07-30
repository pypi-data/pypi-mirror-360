
# PySick

PySick - A Bypass for learning Graphics Development

Classes:
- SickError - Custom error for PySick
- InGine - Main engine/window class
- graphics - Drawing utility class
- message_box - Messagebox utilities

---

## Description

PySick is a lightweight Python library designed to simplify learning graphics development.

It provides easy functions for:

- Creating a window
- Drawing shapes
- Filling the canvas with color
- Collision detection
- Displaying images and videos
- Simple message box dialogs

Built on top of Tkinter, PySick removes boilerplate so you can focus on graphics logic.

---

## Installation

If packaged, install via pip:

```bash
pip install pysick
```

Otherwise, place the `pysick` folder into your Python project directory.

---

## Quick Example

```python
import pysick

# Create a window
game = pysick.InGine(800, 600)

# Create a rectangle shape
rect = pysick.graphics.Rect(50, 50, 200, 100, fill="blue")

# Draw the rectangle
pysick.graphics.draw(game, rect)

# Add a label
game.add_label("Hello, PySick!", 100, 300,
               font=("Arial", 24),
               color="green")

# Start the event loop
game.sickloop()
```

---

## Drawing Shapes

All drawing uses shape objects. Supported shapes:

### Rectangle

```python
rect = pysick.graphics.Rect(
    x=100,
    y=50,
    width=200,
    height=100,
    fill="red"
)
pysick.graphics.draw(game, rect)
```

### Oval

```python
oval = pysick.graphics.Oval(
    x=150,
    y=100,
    width=100,
    height=60,
    fill="purple"
)
pysick.graphics.draw(game, oval)
```

### Circle

```python
circle = pysick.graphics.Circle(
    x=300,
    y=300,
    radius=50,
    fill="yellow"
)
pysick.graphics.draw(game, circle)
```

### Line

```python
line = pysick.graphics.Line(
    x1=50,
    y1=50,
    x2=200,
    y2=200,
    fill="black"
)
pysick.graphics.draw(game, line)
```

---

## Fill the Canvas

To fill the entire canvas with a color:

```python
pysick.graphics.fill_screen(game, "lightblue")
```

---

## Collision Detection

Use `pysick.colliCheck` for collision checks.

### Rectangle vs Rectangle

```python
r1 = pysick.graphics.Rect(10, 10, 50, 50, fill="red")
r2 = pysick.graphics.Rect(30, 30, 60, 60, fill="blue")

if pysick.colliCheck.rectxrect(r1, r2):
    print("Rectangles overlap!")
```

### Circle vs Circle

```python
c1 = pysick.graphics.Circle(100, 100, 30, fill="green")
c2 = pysick.graphics.Circle(120, 120, 30, fill="yellow")

if pysick.colliCheck.circlexcircle(c1, c2):
    print("Circles overlap!")
```

### Rectangle vs Circle

```python
rect = pysick.graphics.Rect(50, 50, 80, 80, fill="pink")
circle = pysick.graphics.Circle(90, 90, 30, fill="purple")

if pysick.colliCheck.rectxcircle(rect, circle):
    print("Rectangle and circle collide!")
```

---

## Displaying Images

Show images on the canvas:

```python
pysick.image.show(game, "my_image.png", x=0, y=0)
```

---

## Playing Videos

Play a video on the canvas:

```python
pysick.image.play(
    game,
    video_path="video.mp4",
    resolution=(640, 480),
    fps=24,
    cleanup=True
)
```

---

## About

Show version info:

```python
pysick.about()
```

