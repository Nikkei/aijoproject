import datetime
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import pandas as pd
from PIL import Image, ImageTk

IMG_SIZE = 720
WINDOW_SIZE = 960


def fit_img_to(img, size=512):
    (h, w) = img.shape[:2]
    if h > w:
        r = size / float(h)
        resized_image = cv2.resize(img, (int(r * w), size))
    else:
        r = size / float(w)
        resized_image = cv2.resize(img, (size, int(r * h)))
    return resized_image


def cv_to_imgtk(img):
    img_copy = img.copy()
    b, g, r = cv2.split(img_copy)
    img_rgb = cv2.merge((r, g, b))
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    return img_tk


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # set the window title
        self.title("Edit Gender")

        # set the window size
        self.geometry(str(WINDOW_SIZE) + "x" + str(WINDOW_SIZE))

        # Set window grid to 1x1
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize path variables
        self.img_dir = None
        self.img_csv_file_path = None

        # key: 1-male, 2-female, 3-undetermined, 4-not-human
        # internally: 0-female(red), 1-male(green), -1 -undetermined(blue), -2
        # -not-human(white)
        self.current_gender_mode = 0

        self.article_id = 0

        # index of saved files to increment file name
        self.save_id = 0
        # -----------------------------------menu_frame-----------------------------
        # create the main page frame
        self.menu_frame = tk.Frame()
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        # create the title label
        self.titleLabel = tk.Label(
            self.menu_frame, text="Edit Gender", font=("Helvetica", "35")
        )
        self.titleLabel.grid(row=0, column=1)
        # button for moving to frame 1
        self.selectFolderButton = tk.Button(
            self.menu_frame,
            text="Select Image Folder",
            command=lambda: self.selectFolder(self.frame1),
        )
        self.selectCSVButton = tk.Button(
            self.menu_frame,
            text="Select csv",
            command=lambda: self.selectCSV(self.frame1),
        )

        self.frameCountText = tk.Entry(self.menu_frame, width=10)
        self.frameCountText.insert(0, "0")

        self.selectFolderButton.grid(row=1, column=0)
        self.selectCSVButton.grid(row=1, column=1)
        self.frameCountText.grid(row=1, column=2)
        # --------------------------------------------------------------------------
        # -----------------------------------frame1---------------------------------
        # create a new frame to move on
        self.frame1 = tk.Frame()
        self.frame1.grid(row=0, column=0, sticky="nsew")

        # start_img  = cv2.imread("nikkei.png")
        # start_img = fit_img_to(start_img, 512)
        # start_imgtk = cv_to_imgtk(start_img)
        # self.imgLabel = tk.Label(self.frame1, image=start_imgtk)
        self.imgLabel = tk.Label(self.frame1)
        self.imgLabel.image = None
        self.imgLabel.pack()

        self.img_count_text = tk.StringVar()
        self.img_count_text.set("Image count placeholder")
        self.img_count = tk.Label(self.frame1, textvariable=self.img_count_text)
        self.img_count.pack()

        self.img_name_text = tk.StringVar()
        self.img_name_text.set("Image file name place hold")
        self.img_name = tk.Label(self.frame1, textvariable=self.img_name_text)
        self.img_name.pack()

        # Bind key actions
        self.bind("<Left>", self.on_leftkey_pressed)
        self.bind("<Right>", self.on_rightkey_pressed)
        self.bind("<ButtonPress-1>", self.on_leftclick)
        self.bind("<Key>", self.on_key_pressed)

        # --------------------------------------------------------------------------

        # show main_frame on the top layer
        self.menu_frame.tkraise()

    def selectFolder(self, page):
        self.img_dir = tk.filedialog.askdirectory()
        print(self.img_dir)
        if self.img_dir is not None and self.img_csv_file_path is not None:

            # Set initial article number
            frameCountText = self.frameCountText.get()
            self.article_id = int(frameCountText)
            while json.loads(self.images_info.loc[self.article_id, "details"]) == []:
                self.article_id += 1

            page.tkraise()
            self.show_current_image()

    def selectCSV(self, page):
        self.img_csv_file_path = tk.filedialog.askopenfilename(
            filetypes=[("csv", "*.csv")]
        )

        self.images_info = pd.read_csv(self.img_csv_file_path)
        img_dir = "{}/images".format("/".join(self.img_csv_file_path.split("/")[:-1]))
        if os.path.isdir(img_dir):
            self.img_dir = img_dir

        if self.img_dir is not None and self.img_csv_file_path is not None:

            # Set initial article number
            frameCountText = self.frameCountText.get()
            self.article_id = int(frameCountText)
            while json.loads(self.images_info.loc[self.article_id, "details"]) == []:
                self.article_id += 1

            page.tkraise()
            self.show_current_image()

    def changePage(self, page):
        page.tkraise()

    def show_current_image(self):

        detections_info = json.loads(self.images_info.loc[self.article_id, "details"])
        article_id = self.images_info.loc[self.article_id, "article_id"]

        image = self.get_img_with_this_id(self.article_id)
        if image is None:
            print(article_id + " not found.")
            return

        image = fit_img_to(image, IMG_SIZE)
        image_h, image_w, _ = image.shape
        image_boxed = image.copy()

        for face_info in detections_info:
            face_bbox = face_info["bbox"]
            gender = face_info["gender"]

            if gender == 1:
                color = (0, 255, 0)
            elif gender == 0:
                color = (0, 0, 255)
            elif gender == -1:
                color = (255, 0, 0)
            elif gender == -2:
                color = (255, 255, 255)

            bbox_offset = 2
            cv2.rectangle(
                image_boxed,
                (
                    int(face_bbox[0] * image_w) - bbox_offset,
                    int(face_bbox[1] * image_h) - bbox_offset,
                ),
                (
                    int(face_bbox[2] * image_w) + bbox_offset,
                    int(face_bbox[3] * image_h) + bbox_offset,
                ),
                color,
                2,
            )

        # Show image
        imgtk = cv_to_imgtk(image_boxed)

        # self.imgLabel.image = imgtk
        # self.imgLabel.pack()

        self.imgLabel.configure(image=imgtk)
        self.imgLabel.image = imgtk

        img_cout_text = str(self.article_id + 1) + "/" + str(len(self.images_info))

        self.img_count_text.set(img_cout_text)

        self.img_name_text.set(str(article_id))

    def on_rightkey_pressed(self, e):

        while True:
            if self.article_id >= len(self.images_info) - 1:
                break
            self.article_id += 1
            if json.loads(self.images_info.loc[self.article_id, "details"]) != []:
                break

        self.show_current_image()

    def on_leftkey_pressed(self, e):

        while True:
            if self.article_id == 0:
                break
            self.article_id -= 1
            if json.loads(self.images_info.loc[self.article_id, "details"]) != []:
                break

        self.show_current_image()

    def on_key_pressed(self, e):
        if e.char == "1":
            self.current_gender_mode = 1
        if e.char == "2":
            self.current_gender_mode = 0
        if e.char == "3":
            self.current_gender_mode = -1
        if e.char == "4":
            self.current_gender_mode = -2

        if e.char == "s":
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
            ftitle, fext = os.path.splitext(self.img_csv_file_path)
            save_file_path = "{ftitle}_reviewed_{timestamp}{fext}".format(
                ftitle=ftitle, timestamp=timestamp, fext=fext
            )
            print(save_file_path)
            self.images_info.to_csv(save_file_path, index=False)
            self.save_id += 1

    def on_leftclick(self, e):

        if self.article_id < 0:
            return
        if self.img_dir is None or self.img_csv_file_path is None:
            return

        image = self.get_img_with_this_id(self.article_id)
        image = fit_img_to(image, IMG_SIZE)
        image_h, image_w, _ = image.shape
        image_boxed = image.copy()

        # top_mergin = (512 - image_h) / 2
        # image sticks to the top for now
        top_mergin = 0
        # left_mergin = (512 - image_w) / 2
        left_mergin = 0

        detections_info = json.loads(self.images_info.loc[self.article_id, "details"])

        for face_info in detections_info:
            face_bbox = face_info["bbox"]
            gender = face_info["gender"]

            bbox_x0 = int(face_bbox[0] * image_w) + left_mergin
            bbox_y0 = int(face_bbox[1] * image_h) + top_mergin
            bbox_x1 = int(face_bbox[2] * image_w) + left_mergin
            bbox_y1 = int(face_bbox[3] * image_h) + top_mergin

            if bbox_x0 <= e.x and e.x <= bbox_x1 and bbox_y0 <= e.y and e.y <= bbox_y1:
                face_info["gender"] = self.current_gender_mode

        self.images_info.loc[self.article_id, "details"] = json.dumps(detections_info)

        self.show_current_image()

    # Return CV image for the id in article_info
    def get_img_with_this_id(self, id):
        kiji_id = self.images_info.loc[id, "article_id"]
        path = self.img_dir + "/" + str(kiji_id) + ".jpg"

        image = cv2.imread(path)

        return image


if __name__ == "__main__":
    app = App()
    app.mainloop()
