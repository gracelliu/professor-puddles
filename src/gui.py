import tkinter as tk
from tkinter import Canvas
from tkinter.ttk import Style, Combobox
import cv2
import json
from main import main
from PIL import Image, ImageTk
from windows_toasts import Toast, WindowsToaster

# Set up toaster for notifs
toaster = WindowsToaster('Python')
newToast = Toast()

LIGHT_MODE = {
    "bg": "white",
    "text": "black",
    "btn": "#f5f5f5",
    "btn_text": "black",
    "dropdown_bg": "white",
    "dropdown_text": "black",
    "highlight": "#e1e1e1"
}

DARK_MODE = {
    "bg": "black",
    "text": "white",
    "btn": "#black",
    "btn_text": "white",
    "dropdown_bg": "white",
    "dropdown_text": "white",
    "highlight": "#666666"
}


class GUI:

    def __init__(self, root, video_source=0):
        self.root = root
        self.root.title("Posture Corrector")
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        self.combo_style = Style()

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)
        self.detector = main()
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 2080)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 4020)

        self.label_widget = tk.Label(root, borderwidth=2, relief="solid")
        self.label_widget.place(relx=0.17, rely=0.05, relwidth=0.8, relheight=0.8)

        self.theme = LIGHT_MODE  # Start with light mode

        self.btn_start = self.create_rounded_button("Start", "light green", self.start, 0.02, 0.25)
        self.btn_stop = self.create_rounded_button("Stop", "#FF8888", self.stop, 0.02, 0.35)
        self.btn_setup = self.create_rounded_button("Setup", "light blue", self.setup, 0.02, 0.45)

        self.btn_theme_toggle = self.create_rounded_button("Toggle Theme", self.theme["btn"], self.toggle_theme, 0.02, 0.45)
        self.btn_theme_toggle.place(relx=0.04, rely=0.05, relwidth=0.15, relheight=0.08)

        dropdown_var = tk.StringVar()
        dropdown_var.set("Configs")

        # Read data from the JSON file
        with open('data.json') as json_file:
            loaded_data = json.load(json_file)["people"]
        dropdown_values = [loaded_data[0]["name"], loaded_data[1]["name"], loaded_data[2]["name"], loaded_data[3]["name"]]

        self.dropdown = self.create_styled_combobox(dropdown_values, 0.15, 0.5)
        self.dropdown.place(relx=0.01, rely=0.1, relwidth=0.1, relheight=0.05)
        self.dropdown.set("Configs")

        self.is_playing = False
        self.update()

        self.apply_theme(self.theme)  # Apply theme on initialization

    def apply_theme(self, theme):
        self.root.configure(bg=theme["bg"])
        self.label_widget.configure(bg=theme["bg"], fg=theme["text"])
        self.btn_theme_toggle.configure(bg=theme["btn"])

        # Configuring the dropdown style
        self.combo_style.configure("TCombobox",
                                   fieldbackground=theme["dropdown_bg"],
                                   background=theme["btn"],
                                   foreground=theme["dropdown_text"],
                                   padding=10,
                                   font=("Helvetica", 12))

    def toggle_theme(self):
        if self.theme == LIGHT_MODE:
            self.theme = DARK_MODE
        else:
            self.theme = LIGHT_MODE

        self.apply_theme(self.theme)

    def create_rounded_button(self, text, color, cmd, relx, rely):
        canvas = Canvas(self.root, bg=self.theme["bg"], bd=0, highlightthickness=0, relief='ridge')
        canvas.place(relx=relx, rely=rely, relwidth=0.15,
                     relheight=0.08)

        # Using create_oval to make the button rounded
        btn_shape = canvas.create_oval(10, 10, 10 + 150, 10 + 40, outline=color, fill=color, width=2)

        btn_id = canvas.create_text(80, 25, text=text, fill=self.theme["btn_text"],
                                    font=("Helvetica", 12))  # Removed "bold"

        # Binding both the shape and the text to the button action
        canvas.tag_bind(btn_shape, '<ButtonPress-1>', lambda event, c=cmd: c())
        canvas.tag_bind(btn_id, '<ButtonPress-1>', lambda event, c=cmd: c())

        return canvas

    def create_styled_combobox(self, values, relx, rely):
        combo_style = Style()
        combo_style.theme_use('clam')
        combo_style.configure("TCombobox",
                              fieldbackground=self.theme["dropdown_bg"],
                              background=self.theme["btn"],
                              foreground=self.theme["dropdown_text"],
                              padding=10,
                              font=("Helvetica", 12))
        combo = Combobox(self.root, values=values, style="TCombobox")
        combo.place(relx=relx, rely=rely, relwidth=0.15)
        return combo

    def start(self):
        if not self.is_playing:
            self.is_playing = True
            self.update()

    def stop(self):
        self.is_playing = False

    def setup(self):
        entry1 = tk.Entry(self.root)
        # canvas1.create_window(200, 140, window=entry1)
        # data
        # with open("data.json", "w") as json_file:
        #     json.dump(data, json_file, indent=4)
        self.setup = False

    def update(self):
        # Capture the video frame by frame

        _, img = self.vid.read()

        # Setup
        img = self.detector.find_pose(img)
        self.detector.get_position(img)  # DO NOT DELETE: this will give the landmark list

        # Interested angle
        # r_turn = self.detector.find_angle(img, 6, 8, 0)
        # l_turn = self.detector.find_angle(img, 3, 7, 0)
        front_posture = self.detector.find_angle(img, 11, 0, 12)
        left_shoulder = self.detector.find_angle(img, 9, 11, 12)
        right_shoulder = self.detector.find_angle(img, 10, 12, 11)

        good_poster = True

        if front_posture < 75 \
                or front_posture > 95 \
                or left_shoulder < 310 or left_shoulder > 320 \
                or right_shoulder < 40 or right_shoulder > 50:
            good_poster = False
        print(good_poster)

        if not good_poster:
            newToast.text_fields = ['!']
            newToast.on_activated = lambda _: print('Toast clicked!')
            toaster.show_toast(newToast)
        # self.detector.showFps(frame)
        opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

        if self.is_playing:
            opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)
            self.label_widget.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


def gui():
    root = tk.Tk()
    root.configure(bg="black")
    root.bind('<Escape>', lambda e: root.quit())
    app = GUI(root)

    root.mainloop()


if __name__ == "__main__":
    gui()
