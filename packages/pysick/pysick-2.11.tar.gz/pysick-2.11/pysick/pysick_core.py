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


SickVersion = "2.11"


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
    PySick drawing utility class for shapes and screen manipulation.
    """

    @staticmethod
    def draw_rect(master, x, y, width, height, fill):
        """
        Draw a rectangle.

        Parameters:
            master (InGine): The InGine instance.
            x (int): Top-left x coordinate.
            y (int): Top-left y coordinate.
            width (int): Rectangle width.
            height (int): Rectangle height.
            fill (str): Fill color.
        """
        try:
            x2 = x + width
            y2 = y + height

            __canvas = master._get_canvas()

            __canvas.create_rectangle(x, y, x2, y2, fill=fill)

        except Exception as ex:
            raise SickError(str(ex))


    @staticmethod
    def fill_screen(master, fill):
        """
        Fill the entire screen with a solid color.

        Parameters:
            master (InGine): The InGine instance.
            fill (str): Color.
        """
        try:
            __canvas = master._get_canvas()
            __canvas.delete("all")
            __canvas.create_rectangle(
                0, 0,
                master.width, master.height,
                fill=fill
            )
        except Exception as ex:
            raise SickError(str(ex))


    @staticmethod
    def draw_oval(master, x, y, width, height, fill):
        """
        Draw an oval shape.

        Parameters:
            master (InGine): The InGine instance.
            x (int): Top-left x coordinate.
            y (int): Top-left y coordinate.
            width (int): Oval width.
            height (int): Oval height.
            fill (str): Fill color.
        """

        try:
            x2 = x + width

            y2 = y + height

            __canvas = master._get_canvas()

            __canvas.create_oval(x, y, x2, y2, fill=fill)

        except Exception as ex:
            raise SickError(str(ex))


    @staticmethod
    def draw_circle(master, x, y, radius, fill):
        """
        Draw a circle.

        Parameters:
            master (InGine): The InGine instance.
            x (int): Center x coordinate.
            y (int): Center y coordinate.
            radius (int): Radius.
            fill (str): Fill color.
        """
        try:
            __canvas = master._get_canvas()
            __canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=fill
            )
        except Exception as ex:
            raise SickError(str(ex))


    @staticmethod
    def draw_line(master, x1, y1, x2, y2, fill):
        """
        Draw a straight line.

        Parameters:
            master (InGine): The InGine instance.
            x1 (int): Starting x coordinate.
            y1 (int): Starting y coordinate.
            x2 (int): Ending x coordinate.
            y2 (int): Ending y coordinate.
            fill (str): Line color.
        """
        try:
            __canvas = master._get_canvas()
            __canvas.create_line(x1, y1, x2, y2, fill=fill)
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
    Collision Detection methods for PySick.
    """

    @staticmethod
    def is_colliding_rect(x1, y1, w1, h1, x2, y2, w2, h2):
        """
        Checks if two rectangles overlap (AABB collision).

        Rect1 = (x1, y1, w1, h1)
        Rect2 = (x2, y2, w2, h2)

        Returns:
            True if overlapping, False otherwise.
        """
        return (
            x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2
        )

    @staticmethod
    def is_colliding_circle(x1, y1, r1, x2, y2, r2):
        """
        Checks if two circles overlap.

        Circle1 = (x1, y1, radius r1)
        Circle2 = (x2, y2, radius r2)

        Returns:
            True if overlapping, False otherwise.
        """
        dx = x2 - x1
        dy = y2 - y1
        distance_squared = dx * dx + dy * dy
        radius_sum = r1 + r2
        return distance_squared < (radius_sum * radius_sum)

    @staticmethod
    def is_colliding_circle_rect(cx, cy, cr, rx, ry, rw, rh):
        """
        Checks if a circle and rectangle overlap.

        Circle center = (cx, cy), radius = cr
        Rectangle = (rx, ry, rw, rh)

        Returns:
            True if overlapping, False otherwise.
        """
        # Find the closest point on the rectangle to the circle center
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (cr * cr)

if __name__ != "__main__":
    print(f"--------------------pysick (v.{SickVersion},2.1.2026), tk(-v{tk.TkVersion}), Tcl(v-3.10) ShellRelease-------------------------")