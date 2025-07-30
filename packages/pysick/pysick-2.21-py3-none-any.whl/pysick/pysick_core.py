"""pysick.py

PySick - An Bypass for learning Graphics Development

Classes:
    SickError - Custom error for PySick
    InGine - Main engine/window class
    graphics - Drawing utility class
    message_box - Messagebox utilities
"""


from . import _tkinter_pysick as tk
from . import _messagebox_pysick as messagebox


SickVersion = "2.21"


try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
except Exception:
    try:
        windll.user32.SetProcessDPIAware()    # Windows Vista+
    except Exception:
        pass


class SickError(Exception):
    """
    Custom error for PySick module.

    Parameters:
        message (str): Optional error message.
    """

    def __init__(self, message="A SickError occurred!"):
        super().__init__(message)


class InGine:
    """
    PySick InGine class for managing the Tkinter window and canvas.

    Parameters:
        width (int): Window width in pixels.
        height (int): Window height in pixels.
    """

    def __init__(self, width, height):
        """Initialize the engine window and canvas."""


        print(f"[pysick] Window Initialized with {width}x{height}")

        self.__root = tk.Tk()
        self.__root.title("pysick graphics")

        self.width = width
        self.height = height
        self.__root.geometry(f"{width}x{height}")

        self.__canvas = tk.Canvas(self.__root, width=width, height=height)
        self.__canvas.pack()

        try:
            #icon_path_yellow = os.path.join(
             #   os.path.dirname(__file__),
              #  r"assets\yellow_icon_2k.ico"
            #)
            #self.__root.iconbitmap(icon_path_yellow)
            import os
            import sys

            py_icon_path = os.path.join(os.path.dirname(sys.executable), 'DLLs', 'pyc.ico')
            try:
                self.__root.iconbitmap(py_icon_path)
            except Exception:
                pass
        except Exception as ex:
            raise SickError(str(ex))

    def _get_canvas(self):
        import inspect
        caller = inspect.stack()[1].frame.f_globals["__name__"]
        if not caller.startswith("pysick."):
            raise SickError(f"Unauthorized access from {caller}")
        return self.__canvas


    def sickloop(self):
        """
        Run the Tkinter main loop.

        Parameters:
            self
        """
        self.__root.mainloop()


    def set_title(self, title):
        """
        Set the window title.

        Parameters:
            title (str): New title for the window.
        """
        self.__root.title(title)


    def lock(self, key, func):
        """
        Bind a function to a keypress event.

        Parameters:
            key (str): The key to bind (e.g. '<Left>').
            func (function): The function to call on key press.
        """
        self.__root.bind(key, lambda event: func())


    def unlock(self, key):
        """
        Unbind a key press.

        Parameters:
            key (str): The key to unbind.
        """
        self.__root.unbind(key)


    def add_label(self, text, x, y, font=("Arial", 14), color="black"):
        """
        Add a text label to the window.

        Parameters:
            text (str): Label text.
            x (int): X coordinate.
            y (int): Y coordinate.
            font (tuple): Font specification, e.g. ("Arial", 14).
            color (str): Text color.
        """
        label = tk.Label(self.__root, text=text, font=font, fg=color)
        label.place(x=x, y=y)


    def add_button(self, text, x, y, func, width=10, height=2):
        """
        Add a clickable button.

        Parameters:
            text (str): Button text.
            x (int): X coordinate.
            y (int): Y coordinate.
            func (function): Function to call on click.
            width (int): Button width.
            height (int): Button height.
        """
        button = tk.Button(
            self.__root,
            text=text,
            command=func,
            width=width,
            height=height
        )
        button.place(x=x, y=y)


    def time_in(self, ms, func):
        """
        Schedule a function to run after a delay.

        Parameters:
            ms (int): Milliseconds delay.
            func (function): Function to run.
        """
        self.__root.after(ms, func)


    def quit(self):
        """
        Destroy the window and quit the program.

        Parameters:
            self
        """
        self.__root.destroy()


class graphics:
    """
    PySick drawing utilities for shapes and screen manipulation.
    """

    class Rect:
        """
        Rectangle shape.
        """
        def __init__(self, x, y, width, height, fill):
            self._shape_type = "rect"
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.fill = fill

    class Oval:
        """
        Oval shape.
        """
        def __init__(self, x, y, width, height, fill):
            self._shape_type = "oval"
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.fill = fill

    class Circle:
        """
        Circle shape.
        """
        def __init__(self, x, y, radius, fill):
            self._shape_type = "circle"
            self.x = x
            self.y = y
            self.radius = radius
            self.fill = fill

    class Line:
        """
        Line shape.
        """
        def __init__(self, x1, y1, x2, y2, fill):
            self._shape_type = "line"
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.fill = fill


    @staticmethod
    def fill_screen(master, fill):
        """
        Fill the entire screen with a solid color.
        """
        canvas = master._get_canvas()
        canvas.delete("all")
        canvas.create_rectangle(
            0, 0,
            master.width,
            master.height,
            fill=fill
        )


    @staticmethod
    def draw(master, shape):
        """
        Draw any shape object.

        Parameters:
            master (InGine): The engine window.
            shape: A shape instance from graphics class.
        """

        canvas = master._get_canvas()

        try:
            shape_type = getattr(shape, "_shape_type", None)

            if shape_type == "rect":
                x2 = shape.x + shape.width
                y2 = shape.y + shape.height
                canvas.create_rectangle(shape.x, shape.y, x2, y2, fill=shape.fill)

            elif shape_type == "oval":
                x2 = shape.x + shape.width
                y2 = shape.y + shape.height
                canvas.create_oval(shape.x, shape.y, x2, y2, fill=shape.fill)

            elif shape_type == "circle":
                canvas.create_oval(
                    shape.x - shape.radius,
                    shape.y - shape.radius,
                    shape.x + shape.radius,
                    shape.y + shape.radius,
                    fill=shape.fill
                )

            elif shape_type == "line":
                canvas.create_line(
                    shape.x1, shape.y1,
                    shape.x2, shape.y2,
                    fill=shape.fill
                )

            else:
                raise SickError("Invalid shape object passed to graphics.draw().")

        except Exception as ex:
            raise SickError(str(ex))



class message_box:
    """
    PySick messagebox utility class.
    """

    @staticmethod
    def ask_question(title, text):
        """
        Show a question dialog.

        Parameters:
            title (str)
            text (str)
        """
        return messagebox.askquestion(title, text)


    @staticmethod
    def show_info(title, text):
        """
        Show an informational dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showinfo(title, text)


    @staticmethod
    def show_warning(title, text):
        """
        Show a warning dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showwarning(title, text)


    @staticmethod
    def show_error(title, text):
        """
        Show an error dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showerror(title, text)


    @staticmethod
    def about(title, text):
        """
        Show an about dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showinfo(title, text)


def about():
    """
    Show PySick about messagebox.

    Parameters:
        -
    """
    messagebox.showinfo(
        "pysick shows: messagebox.about()",
        f"Hello, this is pysick(v.{SickVersion}), tk(-v{str(tk.TkVersion)}), Tcl(v-3.10)"
    )

class image:

    @staticmethod
    def extract_frames(video_path, output_folder, size):

        import os

        os.makedirs(output_folder, exist_ok=True)
        w, h = size
        cmd = f'ffmpeg -i "{video_path}" -vf scale={w}:{h} "{output_folder}/frame_%04d.png"'
        os.system(cmd)

    @staticmethod
    def cleanup_frames(folder):

        import os

        for f in os.listdir(folder):

            os.remove(os.path.join(folder, f))

        os.rmdir(folder)


    @staticmethod
    def play(engine, video_path, resolution=(320, 240), fps=24, cleanup=True):

        """
        Public method to play a video on a given engine (InGine instance).

        Parameters:
            engine      : InGine instance from pysick
            video_path  : Path to video file (.mp4)
            resolution  : Tuple (width, height)
            fps         : Frames per second
            cleanup     : Whether to delete frames after playback
        """
        import os

        canvas = engine.__canvas

        __root = canvas.winfo_toplevel()

        frame_folder = "_video_frames"

        video_path = os.path.abspath(video_path)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"[pysick.video] Video not found: {video_path}")

        image.extract_frames(video_path, frame_folder, resolution)

        frames = sorted(f for f in os.listdir(frame_folder) if f.endswith(".png"))

        if not frames:
            raise RuntimeError("[pysick.video] No frames extracted. ffmpeg may have failed.")

        index = 0

        tk_img = tk.PhotoImage(file=os.path.join(frame_folder, frames[0]))
        img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)

        def advance():

            nonlocal index, tk_img

            if index < len(frames):

                frame_path = os.path.join(frame_folder, frames[index])
                tk_img = tk.PhotoImage(file=frame_path)

                canvas.itemconfig(img_id, image=tk_img)
                canvas.image = tk_img  # avoid garbage collection

                index += 1

                __root.after(int(1000 / fps), advance)

            else:

                if cleanup:
                    image.cleanup_frames(frame_folder)

                print("[pysick.video] Video playback finished.")

        advance()

    @staticmethod
    def show(engine, image_path, x=0, y=0, anchor="nw"):
        """
        Displays an image on the engine's canvas.

        Parameters:
            engine     : InGine instance from pysick
            image_path : Path to the image file (.png, .jpg, etc.)
            x       : Position on canvas
            y       : Position on the canvas
            anchor     : Anchor point (default: "nw" = top-left)
        """

        import os

        if not os.path.exists(image_path):

            raise FileNotFoundError(f"[pysick.photo] Image file not found: {image_path}")

        img = tk.PhotoImage(file=image_path)

        engine.__canvas.create_image(x, y, image=img, anchor=anchor)
        engine.__canvas.image = img  # prevent garbage collection

        print(f"[pysick.photo] Displayed: {image_path}")

class colliCheck:
    """
    PySick collision checking utilities.
    """

    @staticmethod
    def rectxrect(one_rect, another_rect):
        """
        Check if two rectangles collide.

        Parameters:
            one_rect (graphics.Rect)
            another_rect (graphics.Rect)

        Returns:
            bool
        """
        return (
            one_rect.x < another_rect.x + another_rect.width and
            one_rect.x + one_rect.width > another_rect.x and
            one_rect.y < another_rect.y + another_rect.height and
            one_rect.y + one_rect.height > another_rect.y
        )


    @staticmethod
    def circlexcircle(one_circle, another_circle):
        """
        Check if two circles collide.

        Parameters:
            one_circle (graphics.Circle)
            another_circle (graphics.Circle)

        Returns:
            bool
        """
        dx = another_circle.x - one_circle.x
        dy = another_circle.y - one_circle.y
        distance_squared = dx * dx + dy * dy
        radius_sum = one_circle.radius + another_circle.radius

        return distance_squared < radius_sum * radius_sum


    @staticmethod
    def rectxcircle(rect, circle):
        """
        Check if a rectangle and a circle collide.

        Parameters:
            rect (graphics.Rect)
            circle (graphics.Circle)

        Returns:
            bool
        """
        # Find the closest point on the rect to the circle center
        closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
        closest_y = max(rect.y, min(circle.y, rect.y + rect.height))

        dx = circle.x - closest_x
        dy = circle.y - closest_y

        return (dx * dx + dy * dy) < (circle.radius * circle.radius)


if __name__ != "__main__":
    print(f"--------------------pysick (v.{SickVersion},2.1.2026), tk(-v{tk.TkVersion}), Tcl(v-3.10) ShellRelease-------------------------")