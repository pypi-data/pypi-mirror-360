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


SickVersion = "2.10"


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

        import os

        print(f"[pysick] Window Initialized with {width}x{height}")

        self.root = tk.Tk()
        self.root.title("pysick graphics")

        self.width = width
        self.height = height
        self.root.geometry(f"{width}x{height}")

        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()

        try:
            icon_path_yellow = os.path.join(
                os.path.dirname(__file__),
                r"assets\outdated_logo.ico"
            )
            self.root.iconbitmap(icon_path_yellow)
        except Exception as ex:
            raise SickError(str(ex))


    def sickloop(self):
        """
        Run the Tkinter main loop.

        Parameters:
            self
        """
        self.root.mainloop()


    def set_title(self, title):
        """
        Set the window title.

        Parameters:
            title (str): New title for the window.
        """
        self.root.title(title)


    def lock(self, key, func):
        """
        Bind a function to a keypress event.

        Parameters:
            key (str): The key to bind (e.g. '<Left>').
            func (function): The function to call on key press.
        """
        self.root.bind(key, lambda event: func())


    def unlock(self, key):
        """
        Unbind a key press.

        Parameters:
            key (str): The key to unbind.
        """
        self.root.unbind(key)


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
        label = tk.Label(self.root, text=text, font=font, fg=color)
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
            self.root,
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
        self.root.after(ms, func)


    def quit(self):
        """
        Destroy the window and quit the program.

        Parameters:
            self
        """
        self.root.destroy()


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
            master.canvas.create_rectangle(x, y, x2, y2, fill=fill)
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
            master.canvas.delete("all")
            master.canvas.create_rectangle(
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
            master.canvas.create_oval(x, y, x2, y2, fill=fill)
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
            master.canvas.create_oval(
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
            master.canvas.create_line(x1, y1, x2, y2, fill=fill)
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


if __name__ != "__main__":
    print(f"pysick (v.{SickVersion},2.1.2026), tk(-v{tk.TkVersion}), Tcl(v-3.10) Release")


