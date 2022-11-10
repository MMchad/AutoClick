from pickle import TRUE
from threading import Thread
from ttkwidgets.autocomplete import AutocompleteEntry
from tokenize import String
import cv2 as cv
import numpy as np
import pyautogui
import time
import tkinter as TK
from tkinter import ttk
import sys
import os
import tkinter.filedialog as file
from tkinter import messagebox
import keyboard
import threading

#Returns actual path for files after release
def Path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    relative_path = "Assets\\" + relative_path
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Move mouse and click 
def Click(X, Y, Height, Width, Clicks, Button):
    X = int((X + (Width/2)))
    Y = int((Y + (Height/2)))
    pyautogui.click(x = X, y= Y,clicks=Clicks, button= Button)  

#Returns screenshot of screen
def Screenshot():
    Screen = pyautogui.screenshot()
    Screen = cv.cvtColor(np.array(Screen),cv.COLOR_RGB2BGR)
    return Screen

#Compare screenshot to passed image template as argument
def TemplateMatch(Templates, Canny):

    #Take a screenshot
    Screen = Screenshot()
    if Canny:
        Screen = cv.Canny(Screen, 50, 200)
    for Template in Templates:
        if Canny:
            Template = cv.Canny(Template, 50, 200)
        #Comapre templates with screenshot using OPENCV
        Result = cv.matchTemplate(Screen, Template, cv.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(Result)
        #print(maxVal)
        if maxVal > 0.7:
            (TemplateHeight, TemplateWidth) = Template.shape[:2]
            return maxVal, maxLoc, TemplateHeight, TemplateWidth
    return 0,0,0,0

def Validate(value: String, Max, Type): 
    global Started
    if (value.isdigit() and int(value) <= int(Max) and int(value) >= 0) or value == "":
        return True
    return False

def SelectImage():
    global SelectedImage 
    ImagePath = file.askopenfilename(title="Choose an image", 
    filetypes= [('image files', '.png'),
               ('image files', '.jpg'),
               ('image files', '.jpeg'),
               ('image files', '.jfif'),
               ('image files', '.pjpeg'),
               ('image files', '.pjp'),
           ])
    TempImage = cv.imread(ImagePath, 1)
    if TempImage is not None:
        SelectedImage = TempImage

def PreviewImage():
    global SelectedImage
    try:
        _ = SelectedImage
        cv.imshow('Selected Image', SelectedImage)
    except NameError:
        messagebox.showerror("Error", "No image selected. Please browse and select image before previewing.")

def Toggle():
    try:
        global Started, SelectedImage
        _ = SelectedImage
        Started = not Started
        StyleStartStopButtons()
        ToggleOptions()
        if Started:
            event.clear()
            Start()
        else:
            event.set()
    except NameError:
        messagebox.showerror("Error", "No image selected. Please browse and select image before starting.")

def StyleStartStopButtons():
    global StartButtons
    State = "disabled" if Started else "normal"
    StartButtons[0].config(text = "Running" if Started else "Stopped", fg = "green" if Started else "red")
    StartButtons[1].config(relief = "sunken" if Started else "flat", state = "disabled" if Started else "normal", background = "#EBEBE4" if Started else "#E0E0E0")
    StartButtons[2].config(relief = "sunken" if not Started else "flat", state = "disabled" if not Started else "normal", background = "#EBEBE4" if not Started else "#E0E0E0", height= 3)

def ToggleOptions():
    global SpinBoxes, RadioButtons, ImageButtons, ListBoxes, Window
    State = "disabled" if Started else "normal"
    for Type in SpinBoxes:
        if(SpinBoxes[Type].get() == ""):
            DefaultValue = TK.StringVar(Window, "0")
            SpinBoxes[Type].config(state = State, textvariable = DefaultValue)
        else:
            SpinBoxes[Type].config(state = State)
    for Button in RadioButtons:
        Button.config(state = State)
    for Button in ImageButtons:
        Button.config(state = State)
    for ListBox in ListBoxes:
        ListBox.config(state = "disabled" if Started else "readonly")

def Start():
    
    AutoCLickThread = Thread(target = AutoClick, daemon= True)
    AutoCLickThread.start()

def AutoClick():
    global SpinBoxes, Repeat, event, ClickType, MouseButton, StartButtons
    ClickType.set("Double")
    Iteration = 0
    Range = int(SpinBoxes["RepeatCount"].get())
    Delay = 0
    Count = 0
    while Iteration <= Range and Started and not event.wait(timeout = Delay):
        Count+=1
        Delay = GetDelay()
        if Repeat.get() == "Repeat":
            StartButtons[0].configure(text = "Running\n{Iteration}/{RepeatCount}".format(Iteration = Iteration, RepeatCount = Range))
            Iteration+=1 
        else:
            StartButtons[0].configure(text = "Running\n{Iteration}".format(Iteration = Count))
        maxval,maxLoc,TemplateHeight,TemplateWidth= TemplateMatch([SelectedImage],TRUE)
        if maxval > 0.65:
            Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth, 1 if ClickType.get() == "Single" else 2, "primary" if MouseButton.get() == "Left" else "secondary")
            pyautogui.moveTo(x=10, y=10)
    if Repeat.get()  == "Repeat" and Started:
        Toggle()

def GetDelay():
    global SpinBoxes
    Delay = 0
    Delay += int(SpinBoxes["Hour"].get()) * 60 * 60
    Delay += int(SpinBoxes["Minute"].get()) *60
    Delay += int(SpinBoxes["Second"].get())
    Delay += int(SpinBoxes["Millisecond"].get()) / 1000
    return Delay

def DetectKeyPress():
    while True:
        keyboard.wait("F2")
        Toggle()

#################################################################       


DetectKeyPressThread = Thread(target = DetectKeyPress, daemon= True)
DetectKeyPressThread.start()
event = threading.Event()

################################################################# GUI Stuff

Window = TK.Tk()
Window.resizable(False,False)
Window.title("Auto Click")
Window.configure(background = "grey13")
Repeat = TK.StringVar(Window, "Infinite")
MouseButton = TK.StringVar(Window, "Left")
ClickType = TK.StringVar(Window, "Single")
SelectedImage : None
Started = False
StartButtons = []
SpinBoxes = {}
RadioButtons = []
ListBoxes = []
ImageButtons = []


####################################################### Interval

IntervalLabelFrame = TK.LabelFrame(Window, text="Interval",background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
IntervalLabelFrame.pack(fill="both", expand="yes", padx=10, pady=10)


Row1 = TK.Frame(IntervalLabelFrame,background  = "grey13")
Row1.pack(side="top",fill="x", padx= 5, pady= 8)

HourInterval = TK.Spinbox(Row1, width=5, state = "disabled" if Started else "normal" ,from_=0, to=24,validate="all",vcmd = (Window.register(Validate), '%P', 5, "Hour") , font = ('Open Sans', 12, 'bold'), repeatinterval=25)
HourInterval.pack(side="left", padx= 3)

SpinBoxes["Hour"] = HourInterval

HourLabel = TK.Label(Row1, text= "Hours", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
HourLabel.pack(side="left", padx= 3)

MinuteInterval = TK.Spinbox(Row1, width=5, state = "disabled" if Started else "normal" ,from_=0, to=59,validate="all",vcmd = (Window.register(Validate), '%P', 59, "Minute"), font = ('Open Sans', 12, 'bold'), repeatinterval=25)
MinuteInterval.pack(side="left", padx= 3)

SpinBoxes["Minute"] = MinuteInterval

MinuteLabel = TK.Label(Row1,text= "Minutes", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
MinuteLabel.pack(side="left", padx= 3)

SecondInterval = TK.Spinbox(Row1, width=5, state = "disabled" if Started else "normal" , from_=0, to=59,validate="all",vcmd = (Window.register(Validate), '%P', 59, "Second") , font = ('Open Sans', 12, 'bold') , repeatinterval=25)
SecondInterval.pack(side="left", padx= 3)

SpinBoxes["Second"] = SecondInterval

SecondLabel = TK.Label(Row1, text= "Seconds", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
SecondLabel.pack(side="left", padx= 3)

MillisecondInterval = TK.Spinbox(Row1, width=5, state = "disabled" if Started else "normal" , from_=0, to=999,validate="all",vcmd = (Window.register(Validate), '%P', 999, "Millisecond") , font = ('Open Sans', 12, 'bold'), repeatinterval=4)
MillisecondInterval.pack(side="left", padx= 3)

SpinBoxes["Millisecond"] = MillisecondInterval

MillisecondLabel = TK.Label(Row1, text= "Milliseconds", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
MillisecondLabel.pack(side="left", padx= 3)

####################################################### Container for Click Options and Repeat

Container = TK.Frame(Window, background="grey13")
Container.pack(fill="both", expand="yes")

####################################################### Repeat

RepeatLabelFrame = TK.LabelFrame(Container, text="Repeat",background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
RepeatLabelFrame.pack( side= "right", padx=10, pady=10)

Row1 = TK.Frame(RepeatLabelFrame,background  = "grey13")
Row1.pack(side="top",fill="x", padx= 5, pady= 8)

RepeatCountButton = TK.Radiobutton(Row1, text = "Repeat", state = "disabled" if Started else "normal" , variable = Repeat, value = "Repeat", background = "grey13", fg = "white", font = ('Open Sans', 12, 'bold'), selectcolor= "grey13", activebackground='grey13', activeforeground="white")

RadioButtons.append(RepeatCountButton)

RepeatCountButton.pack(side= "left", padx= 3)

RepeatCount = TK.Spinbox(Row1, width=5, state = "disabled" if Started else "normal" , from_=0, to=10000,validate="all",vcmd = (Window.register(Validate), '%P', 1000, "RepeatCount"),font = ('Open Sans', 12, 'bold'),repeatinterval= 15)
RepeatCount.pack(side= "left", padx= 3)

SpinBoxes["RepeatCount"] = RepeatCount

RepeatCountLabel = TK.Label(Row1, text= "Times", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
RepeatCountLabel.pack(side= "left", padx= 3)

Row2 = TK.Frame(RepeatLabelFrame,background  = "grey13")
Row2.pack(side="top",fill="x", padx= 5, pady= 8)

RepeatUntilStoppedButton = TK.Radiobutton(Row2, state = "disabled" if Started else "normal" , text = "Repeat until stopped", variable = Repeat, value = "Infinite", background = "grey13", fg = "white", font = ('Open Sans', 12, 'bold'), selectcolor= "grey13", activebackground='grey13', activeforeground="white")
RepeatUntilStoppedButton.pack(side= "left", padx= 3)

RadioButtons.append(RepeatUntilStoppedButton)

####################################################### Click Options



ClickOptionsLabelFrame = TK.LabelFrame(Container, text="Click Options", width = 100, background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
ClickOptionsLabelFrame.pack(padx=10, pady=10, side= "left")

Row1 = TK.Frame(ClickOptionsLabelFrame,background  = "grey13")
Row1.pack(side="top",fill="x", padx= 5, pady= 8)

MouseButtonLabel =  TK.Label(Row1, text= "Mouse Button: ", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
MouseButtonLabel.pack(side= "left", padx= 3)

MouseButtonListBox = ttk.Combobox(Row1, state = "disabled" if Started else "readonly" , textvariable = MouseButton, validate="all", font = ('Open Sans', 10))
MouseButtonListBox['values'] = ('Left', 'Right')
MouseButtonListBox.pack(side= "right", padx= 3)

ListBoxes.append(MouseButtonListBox)


Row2 = TK.Frame(ClickOptionsLabelFrame,background  = "grey13")
Row2.pack(side="top",fill="x", padx= 5, pady= 8)

ClickTypeLabel =  TK.Label(Row2, text= "Click Type: ", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
ClickTypeLabel.pack(side= "left", padx= 3)

ClickTypeListBox = ttk.Combobox(Row2, state = "disabled" if Started else "readonly" , textvariable = ClickType, validate="all", font = ('Open Sans', 10))
ClickTypeListBox['values'] = ('Single', 'Double')
ClickTypeListBox.pack(side= "right", padx= 3)

ListBoxes.append(ClickTypeListBox)

####################################################### Container for Click Options and Repeat

Container = TK.Frame(Window, background="grey13")
Container.pack(fill="both", expand="yes")

####################################################### Image Select
def OnPressed(Temp):
    print(Temp)
    return

ImageFrame = TK.LabelFrame(Container, text="Image", width = 100, background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
ImageFrame.pack(padx=10, pady=10, side= "left")

Row1 = TK.Frame(ImageFrame,background  = "grey13")
Row1.pack(side="top",fill="x", padx= 5, pady= 8)

ImageLabel =  TK.Label(Row1, text= "Select Image: ", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'))
ImageLabel.pack(side= "left", padx= 3)

ViewButton = ttk.Button(Row1,text="Preview", command= PreviewImage)
ViewButton.pack(side= "right", padx= 3)

ImageButtons.append(ViewButton)

BrowseButton = ttk.Button(Row1,text="Browse" ,  command= SelectImage, )
BrowseButton.pack(side= "right", padx= 3)

ImageButtons.append(BrowseButton)

StartButtons.append(TK.Label(Container, text= "Running" if Started else "Stopped", background = "grey13",foreground = "white", font = ('Open Sans', 12, 'bold'), fg="green" if Started else "red"))
StartButtons[0].pack(side= "right", padx= (3, 10))


StartButtons.append(TK.Button(Container,text="Start (F2)" , state = "disabled" if Started else "normal" , font = ('Open Sans', 10, 'bold'), command= Toggle, height= 3, background = "#CACACC" if Started else "#E0E0E0", relief="sunken" if  Started else "flat"))
StartButtons[1] .pack(side= "left", padx= (67,3))

StartButtons.append(TK.Button(Container,text="Stop (F2)" , state = "disabled" if not Started else "normal" , font = ('Open Sans', 10, 'bold'), command= Toggle, background = "#CACACC" if not Started else "#E0E0E0", height= 3, relief="sunken" if not Started else "flat"))
StartButtons[2] .pack(side= "left", padx= 3)






Window.mainloop()

#################################################################
