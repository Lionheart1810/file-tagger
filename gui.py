from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import logging
from enum import Enum

class GuiMain(object):

    def __init__(self, args):
        self.__master = Tk()
        self.__master.title("file-tagger")
        self.__args = args
        self.__base = StringVar(self.__master, value=args["base"])
        self.__file_dir = StringVar(self.__master, value=args["file_dir"])
        self.__predict_images = BooleanVar(self.__master, value=args["predict_images"])
        self.__predict_images_top = StringVar(self.__master, value=str(args["predict_images_top"]))
        self.__gui_tag = BooleanVar(self.__master, value=args["gui_tag"])
        self.__open_system = BooleanVar(self.__master, value=args["open_system"])
        self.__index = StringVar(self.__master, value=str(args["index"]))

        validate_number = (self.__master.register(self.__validate_number))

        Label(self.__master, text="Base directory with database:").grid(row=0, column=0)
        Entry(self.__master, textvariable=self.__base).grid(row=0, column=1, columnspan=2)
        Button(self.__master, text="Browse", command=lambda: self.__browse(self.__base)).grid(row=0, column=3)
        Label(self.__master, text="File directory for walking:").grid(row=1, column=0)
        Entry(self.__master, textvariable=self.__file_dir).grid(row=1, column=1, columnspan=2)
        Button(self.__master, text="Browse", command=lambda: self.__browse(self.__file_dir)).grid(row=1, column=3)
        Checkbutton(self.__master, text="Use prediction for image tagging", variable=self.__predict_images).grid(row=2, column=0, columnspan=4, sticky=W)
        Label(self.__master, text="Number of top results:").grid(row=3, column=0)
        Entry(self.__master, textvariable=self.__predict_images_top, validate='all', validatecommand=(validate_number, '%P')).grid(row=3, column=1, columnspan=1)
        Checkbutton(self.__master, text="Show GUI for tagging", variable=self.__gui_tag).grid(row=4, column=0, columnspan=4, sticky=W)
        Checkbutton(self.__master, text="Open all files with system default", variable=self.__open_system).grid(row=5, column=0, columnspan=4, sticky=W)
        Label(self.__master, text="Start at index:").grid(row=6, column=0)
        Entry(self.__master, textvariable=self.__index, validate='all', validatecommand=(validate_number, '%P')).grid(row=6, column=1, columnspan=1)
        Button(self.__master, text="Start", command=self.__master.destroy).grid(row=7, column=0, columnspan=4)

    def loop(self):
        self.__master.mainloop()

        self.__args["base"] = self.__base.get()
        self.__args["file_dir"] = self.__file_dir.get()
        self.__args["predict_images"] = self.__predict_images.get()
        self.__args["predict_images_top"] = int(self.__predict_images_top.get())
        self.__args["gui_tag"] = self.__gui_tag.get()
        self.__args["open_system"] = self.__open_system.get()
        self.__args["index"] = int(self.__index.get())
        return self.__args

    def __browse(self, filepath):
        filename = filedialog.askdirectory()
        filepath.set(filename)

    def __validate_number(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

class GuiTag(object):
    RETURN_NEXT = 0
    RETURN_ABORT = 1

    def __init__(self, index, file, tags):
        self.__ret = self.RETURN_NEXT
        self.__master = Tk()
        self.__master.title("Tag file {}".format(file))
        self.__tags = StringVar(self.__master, value=','.join(tags))
        Label(self.__master, text="Index: {}".format(index)).grid(row=0, column=0, columnspan=2)
        Label(self.__master, text="File: {}".format(file)).grid(row=1, column=0, columnspan=2)
        Entry(self.__master, textvariable=self.__tags).grid(row=2, column=0, columnspan=2, sticky="we")
        Button(self.__master, text="Next", command=self.__handle_next).grid(row=3, column=0)
        Button(self.__master, text="Abort", command=self.__handle_abort).grid(row=3, column=1)

    def loop(self):
        self.__master.mainloop()
        return (self.__ret, self.__tags.get().split(","))

    def __handle_next(self):
        self.__ret = self.RETURN_NEXT
        self.__master.destroy()

    def __handle_abort(self):
        self.__ret = self.RETURN_ABORT
        self.__master.destroy()

class GuiImage(object):
    RETURN_NEXT = 0,
    RETURN_ROTATE_90_COUNTERCLOCKWISE = 1,
    RETURN_ROTATE_90_CLOCKWISE = 2,
    RETURN_ABORT = 3

    def __init__(self, index, file, img, tags):
        self.__ret = self.RETURN_NEXT
        self.__master = Tk()
        self.__master.title("Tag file {}".format(file))
        self.__tags = StringVar(self.__master, value=','.join(tags))
        self.__image_pil = Image.fromarray(img)
        self.__image = ImageTk.PhotoImage(image=self.__image_pil)
        Label(self.__master, text="Index: {}".format(index)).grid(row=0, column=0, columnspan=4)
        Label(self.__master, text="File: {}".format(file)).grid(row=1, column=0, columnspan=4)
        self.__label = Label(self.__master, width=800, height=800, image=self.__image)
        self.__label.grid(row=2, column=0, columnspan=4)
        Entry(self.__master, textvariable=self.__tags).grid(row=3, column=0, columnspan=4, sticky="we")
        Button(self.__master, text="↺", command=self.__handle_rotate_90_counterclockwise).grid(row=4, column=0)
        Button(self.__master, text="↻", command=self.__handle_rotate_90_clockwise).grid(row=4, column=1)
        Button(self.__master, text="Next", command=self.__handle_next).grid(row=4, column=2)
        Button(self.__master, text="Abort", command=self.__handle_abort).grid(row=4, column=3)

    def loop(self):
        self.__master.mainloop()
        return (self.__ret, self.__tags.get().split(","))

    def __handle_rotate_90_counterclockwise(self):
        self.__image_pil = self.__image_pil.rotate(90)
        self.__image = ImageTk.PhotoImage(image=self.__image_pil)
        self.__label.config(image=self.__image)
    
    def __handle_rotate_90_clockwise(self):
        self.__image_pil = self.__image_pil.rotate(-90)
        self.__image = ImageTk.PhotoImage(image=self.__image_pil)
        self.__label.config(image=self.__image)

    def __handle_next(self):
        self.__ret = self.RETURN_NEXT
        self.__master.destroy()

    def __handle_abort(self):
        self.__ret = self.RETURN_ABORT
        self.__master.destroy()
