import tkinter as tk
import os
from PIL import Image, ImageOps
from tkinter import font as tkFont  # Импорт модуля для работы со шрифтами


# Определение цветов
DARK_GRAY = "#2B2B2B"
LIGHT_GRAY = "#D3D3D3"
WHITE = "#FFFFFF"
BUTTON_COLOR = "#2B2B2B"
TEXT_COLOR = "#FFFFFF"


class options():
    def __init__(self, title:str, message:str, choices:list, icon=None, position=None) -> None:
        """
        Initialize the window

        Args:
            title (str): window title
            message (str): message to be shown
            choices (list): list of choices
        """
        # Create window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        self.root.geometry(position)
        self.root.config(bg=DARK_GRAY)  # Установка цвета фона окна
        self.root.wm_minsize(250, 50)
        self.root.attributes('-topmost', True) # Always on top
        # self.root.wm_attributes('-toolwindow', 'True') # Remove the icon, minimize and maximize buttons
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Key>", self.key_pressed_in_root)
        # Frame for the message
        frmLabel = tk.Frame(self.root, background=DARK_GRAY)

        if icon:
            imagepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", icon)
            inverted_image_path = imagepath + '_inverted.png'

            if not os.path.exists(inverted_image_path):
                self.invert_image_colors(imagepath + '.png', inverted_image_path)

            #self.root.iconbitmap(inverted_image_path)

            icon_image = tk.PhotoImage(file=inverted_image_path)
            self.root.iconphoto(True, icon_image)

            image = tk.PhotoImage(file=inverted_image_path)
            titleImg = tk.Label(frmLabel, image=image, background=DARK_GRAY)
            titleImg.image = image  # Храним ссылку на изображение
            titleImg.pack(side=tk.LEFT, anchor=tk.N, padx=(15, 3), pady=15)

        wraplength = 400 if len(choices) < 3 else 650

        message_font = tkFont.Font(size=12, weight='bold')  # Установка размера шрифта и жирного стиля
        titleMsg = tk.Label(frmLabel, text=message, bg=DARK_GRAY, fg=TEXT_COLOR, justify=tk.LEFT, wraplength=wraplength, font=message_font)  # Применение шрифта к тексту
        titleMsg.pack(side=tk.LEFT, padx=(3, 15), pady=15)
        frmLabel.pack(expand=True, fill=tk.BOTH)
        # Frame for the buttons
        frmButtons = tk.Frame(self.root, bg=DARK_GRAY)
        self.buttons = []

        for choice in choices:
            btn = tk.Button(frmButtons, text=choice, borderwidth=1, padx=20, command=lambda x=choice: self.set_choice(self.root, x))
            btn.config(bg=BUTTON_COLOR, fg=WHITE, activebackground=BUTTON_COLOR, activeforeground=WHITE)
            btn.pack(side=tk.LEFT, padx=10, pady=10, ipadx=5, ipady=1)
            self.buttons.append(btn)
        self.buttons[0].focus_set()
        frmButtons.pack(expand=True)
        # Set focus on the window
        self.root.after(300, lambda: [self.root.focus_force(), self.buttons[0].focus_set()])
        # Start the window
        self.root.mainloop()

    def invert_image_colors(self, original_path, inverted_path):
        """
        Inverts the colors of an image and saves it.

        Args:
            original_path (str): The path to the original image.
            inverted_path (str): The path to save the inverted image.
        """
        with Image.open(original_path) as img:
            # Преобразование изображения в режим RGB, если оно в режиме RGBA
            if img.mode == 'RGBA':
                r, g, b, a = img.split()
                rgb_image = Image.merge('RGB', (r, g, b))

                # Инвертирование RGB части
                inverted_rgb = ImageOps.invert(rgb_image)

                # Объединение инвертированной RGB части и альфа-канала обратно
                inverted_img = Image.merge('RGBA', (*inverted_rgb.split(), a))
            else:
                # Инвертирование для других режимов
                inverted_img = ImageOps.invert(img)

            # Сохранение инвертированного изображения
            inverted_img.save(inverted_path)

    def set_choice(self, root:tk.Tk, choice:str) -> str:
        """
        Set the choice and close the window

        Args:
            root (tkinter.Tk): root window
            choice (str): choice

        Returns:
            str: choice
        """
        self.choice = choice
        root.destroy()
        return choice

    def close(self):
        """
        Close the window and set the choice to None
        """
        self.choice = None
        self.root.destroy()

    def key_pressed_in_root(self, event):
        """
        Handles keystrokes in the window for UI updates

        Args:
            event (event): key press event
        """
        # Escape
        if event.keycode == 27:
            self.root.destroy()

    def button_pressed_key(self, event):
        """
        Handles button key presses for UI updates

        Args:
            event (event): key press event
        """
        # Enter
        if event.keycode == 13:
            self.set_choice(self.root, event.widget['text'])
        # Down or Right
        if event.keycode == 40 or event.keycode == 39:
            self.next_button(event.widget)
        # Up or Left
        if event.keycode == 38 or event.keycode == 37:
            self.previous_button(event.widget)

    def next_button(self, button):
        """
        Select the next button

        Args:
            button (button): current button
        """
        i = self.buttons.index(button)
        if i < len(self.buttons) - 1:
            self.buttons[i + 1].focus_set()
        else:
            self.buttons[0].focus_set()

    def previous_button(self, button):
        """
        Sekect the previous button

        Args:
            button (button): current button
        """
        i = self.buttons.index(button)
        if i > 0:
            self.buttons[i - 1].focus_set()
        else:
            self.buttons[-1].focus_set()
