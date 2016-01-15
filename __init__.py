'''
Created on Dec 10, 2011

@author:

Main GUI file
'''

# Handle all imports here, assure that it is backwards version compatible
import time
from Serve import *
from Client import *

try: # Python 3.2
    import tkinter as Tk
    from tkinter import messagebox as tkMessageBox
    from tkinter import font as tkFont
    from tkinter import dnd as Tkdnd
    from tkinter import tkFileDialog as tkFileDialog
except ImportError: # Python 2.7
    import Tkinter as Tk
    import tkMessageBox
    import tkFont
    import Tkdnd # May not be working
    import tkFileDialog


import math
from threading import Thread as Thread
import sys
import shelve
#import json

'''TODO: Fix compression - Why can't it take a string?'''
compress = lambda x: x
decompress = lambda x: x



#self.frame.pack_propagate(0) #no shrinking!



# Declare some high-level program constants
top = Tk.Tk()
top.title("GFile Trade")
PHEIGHT = 600
PWIDTH = 600
PCOLOR1 = "navy blue"
BANCOL  = "black"
BANTEXT = "light blue"
GFILEFONT = ("Arial","15","bold")


# Declare get/set preferences file functions
def getPref(prefname):
    shelf = shelve.open("Prefs.dat")
    if shelf.has_key(prefname):
        item = shelf[prefname]
    else: item = None
    shelf.close()
    return item
    
def savePref(prefname,prefvalue):
    shelf = shelve.open("Prefs.dat")
    shelf[prefname] = prefvalue
    shelf.sync() # Save
    shelf.close()

# Get/Set preference for File Save Directory if exists
import os
SELECTED_DIRECTORY = getPref("savedDirectory")
if SELECTED_DIRECTORY is None:
    SELECTED_DIRECTORY = str(os.getenv("%USERPROFILE%"))+os.sep+"Desktop"
if SELECTED_DIRECTORY == "None"+os.sep+"Desktop":
    SELECTED_DIRECTORY = ""

favdir = Tk.StringVar()
favdir.set(SELECTED_DIRECTORY)

def selectDir(Event):
    chosenDir = tkFileDialog.askdirectory()
    #tkMessageBox.showinfo("k",chosenDir+"\n^ChosenDir") #DEBUG
    if chosenDir is not None and len(chosenDir):
        savePref("savedDirectory",chosenDir)
        favdir.set( chosenDir )




# Set Operating System specific information
# i.e. font size and background color
def rgb2hex(r,g,b):
    return '#%02X%02X%02X'%(r,g,b)

winGray = rgb2hex(204,204,204)

    
if sys.platform == "darwin":
    top.config(bg=winGray,highlightbackground=winGray)
    OS = "MAC"
    headFnt = "40"
elif sys.platform == "win32":
    OS = "WINDOWS"
    headFnt = "30"
    GFILEFONT = ("Arial","11","bold")
elif sys.platform.startswith('linux'): #linux, linux2, linux3
    OS = "LINUX"
    headFnt = "30" 

top.config(width=PWIDTH,height=PHEIGHT)




# Set up GUI Frame1 as THE MAIN FRAME and other GUI setup

frame1 = Tk.Frame(top,bg=PCOLOR1)
frame1.place(relx=0,rely=0,width=PWIDTH,height=PHEIGHT)
Tk.Frame(frame1,bg=BANCOL,width=PWIDTH,height=PHEIGHT*.1).place(relx="0.0",rely="0.0")
labelheader = Tk.Label(frame1,text="GFile Trade",
                       font=("Arial",headFnt,"bold"),bg=BANCOL,fg=BANTEXT)
labelheader.place(relx="0.3",rely="0.01")

dropLabel = Tk.Label(frame1,text="Click here to choose File",font=GFILEFONT,
                     bg="white smoke",padx=30,pady=30)


dirHeader = Tk.Label(frame1, text="Click to change directory\n your downloads go to..."
                     ,font=GFILEFONT,bg="white",fg="black",padx=10,pady=8)
dirHeader.place(relx="0.5",rely="0.1")
dirHeader.bind("<Button-1>",selectDir,True)
dirLabel = Tk.Label(frame1, textvariable=favdir,
                    font=GFILEFONT,padx=10,pady=8,bg="white",fg="black")
dirLabel.bind("<Button-1>",selectDir,True)
dirLabel.place(relx="0.5",rely="0.19")



# Class to handle the GUI updating of files' transfer operations
class ProgHandler(Thread):
    COUNT = 0
    def __init__(self,filename=None,size=None,mode=None):
        Thread.__init__(self)
        self.daemon = True
        if filename is None:
            return
        self.name = filename
        self.mode = mode
        self.size = size
        self.ID = ProgHandler.COUNT +1
        ProgHandler.COUNT += 1
        self.progressLabel = Tk.Label(frame1,text=("Preparing..."+filename)
                                      ,bg="light blue",fg="black",padx=10,pady=10)
        
        self.progressLabel.place(relx="0.5",rely="0."+str(4+((self.ID)%5)))
    def run(self):
        pass
    def onProgress(self,datatransferred):
        perc = int(   100.0*(float(datatransferred)/self.size)    )
        self.progressLabel.config(text="File "+self.name+" "+str(perc)+"% "+self.mode
                                  ,bg="light blue")
        
    def onFinish(self):            
        pr("onFinish fired")
        self.progressLabel.bind("<Button-1>",lambda Event:self.progressLabel.place_forget(),True)
        self.progressLabel.config(bg="light green",text=self.name+" transferred successfully!")
        #ProgHandler.COUNT -= 1
        
    def onFailure(self):
        self.progressLabel.bind("<Button-1>",lambda Event:self.progressLabel.place_forget(),True)
        self.progressLabel.config(bg="salmon",text=self.name+" failed to send!")



def getFileName(Event):
    def startSend():
        pr("IN STARTSEND")

        global conObject
        try:            
            pr("length of filenametuple:" + str(len(filenameTuple)))
            for aFilename in filenameTuple:
                if len(aFilename) > 0:
                    conObject.fileOperation("send",aFilename);
                    pr("conObject.fileOperationSEND")
        except Exception as ex:
            pr("conObject is NONE:" + str(ex))
        
    def clickSendHandle(Event):
        Thread(target=startSend,args=()).start()
        sendBTN.place_forget()
        dropLabel.config(text="Click here to send a file!")
    
    """ TODO: DECLARE HOW MANY FILES AND/OR DIRECTORIES TO SEND
        THOUGHT: if is_dir JUST ZIP AND SEND? """
        
    #filetypes=[('TAR & tarballs','*.tar *.tar.gz'),('All Files','*.*')]
    
    filenameTuple = [tkFileDialog.askopenfilename(),]
    pr(str(filenameTuple)+"<--filename os.sep->"+os.sep)
    
    # Verify name and bind action to sendBTN
    if(len(filenameTuple) and len(filenameTuple[0]) ):
        dropLabel.config(text=str("\n".join(filenameTuple)))
        sendBTN = Tk.Label(frame1,text="Send!",bg="blue",
                           fg="white",padx=10,pady=10,font=GFILEFONT)
        sendBTN.bind("<Button-1>",clickSendHandle,True)
        sendBTN.place(relx="0.12",rely="0.5")


dropLabel.bind("<Button-1>",getFileName,True)


# Bind this StringVar to always be the value of the box where nums are entered
fiveDigit = Tk.StringVar()
fiveDigit.set( compress(  Comm.ip  ) )

# Initialize GUI items only used in server mode
DCBUTTON = Tk.Label(frame1,text="Disconnect",bg="red",fg="white",font=GFILEFONT,padx=10,pady=4)
numFrame = Tk.Frame(frame1,width=PWIDTH-250-75,height=PHEIGHT-150,bg="white")
numFrame.place(relx="0.5",rely="0.1")

# Initialize GUI items only used in client mode
#numFrame = Tk.Frame(frame1,width=PWIDTH-250-75,height=PHEIGHT-150,bg="white")
errorlabel = Tk.Label(numFrame,font=("Arial","16","bold"),fg="red")
numlabel = Tk.Label(numFrame,text="Enter the number from the other\n computer here")
numentry = Tk.Entry(numFrame,borderwidth=5,textvariable=fiveDigit)


# If server mode, this connection event fires
def srOnConnect():
    dropLabel.place(relx="0.05",rely="0.27")
    unmap(numFrame)
    unmap(routerLabel)

    

# GUI labels to show what to enter on the other computer to connect
showNumlabel = Tk.Label(numFrame,text="Enter this number on\nthe other computer to connect")
thenum = Tk.Label(numFrame,text=compress( Comm.ip  ),
                          font=("Arial","20","bold"),fg="green")

# FIX for place_forget failing on Windows.
def unmap(tkinterWidget):
    if OS == "WINDOWS":
        tkinterWidget.place(relx="8",rely="8")
    else: # This is for Mac, and Linux. place_forget might not work on Linux
        tkinterWidget.place_forget()

# Fired when the connection is dropped
def handleDC(Event):
    global conObject
    if conObject is not None: conObject.close()
    conObject = None

    buttonFrame.place(relx="0.5",rely="0.1")
    unmap(numFrame)
    unmap(numlabel) # Client only
    unmap(dropLabel)
    unmap(DCBUTTON)
    errorlabel.config(text="Disconnected")
    errorlabel.place(relx="0.5",rely="0.2")
    unmap(routerLabel)
    # Server only
    unmap(showNumlabel)
    unmap(thenum)
    # Client only
    unmap(numentry)
    unmap(submitnum)

DCBUTTON.bind("<Button-1>",handleDC,True)
    
# Set initializations
conObject = None
Comm.srOnConnect = srOnConnect
Comm.onDisconnect = handleDC

routerLabel = Tk.Label(frame1,
    text="""Sorry, you are behind a personal router. and cannot trade files with anyone outside
    of your home network.       i.e. your house.""",font=GFILEFONT,bg="white",fg="black")

# If we are the server, this fires
def beTheServer():
    try:
        global conObject
        DCBUTTON.place(relx="0.1",rely="0.8")
        
        conObject = Serve() #Takes in onConnect and onDisconnect
        conObject.favdir = favdir
        conObject.PROGCLASS = ProgHandler

        # Create Box GUI for 5 digit number
        buttonFrame.place_forget()
        showNumlabel.place(relx="0.0",rely="0.0")
        thenum.place(relx="0.1",rely="0.1")
        numFrame.place(relx="0.5",rely="0.1")
        numlabel.place(relx="0.0",rely="0.0")
        
        #sr.onConnect = srOnConnect
        #sr.onDisconnect = handleDC
        
        #Start hosting a socket and check for router issues
        conObject.start()
        pr("Comm.routerflag = " + str(Comm.routerflag))
        if Comm.routerflag == True:
            routerLabel.place(relx="0.01",rely="0.9")
        elif Comm.routerflag == False:
            pass
        else: #routerflag is None
            pr("Routerflag isn't even SET!")
        
    except ValueError as ex:
        pr("That socket's in use: "+str(ex))
        errorlabel.config(text="Can't bind socket? Is it already in use")
        errorlabel.place(relx="0.5",rely="0.2")

# This fires if we are the client
def beTheClient():
    buttonFrame.place_forget()
    
    # ASK FOR NUMBER
    numFrame.place(relx="0.5",rely="0.1")
    numlabel.place(relx="0.0",rely="0.0")
    numentry.place(relx="0.2",rely="0.1")
    submitnum.place(relx="0.25",rely="0.18")
    DCBUTTON.place(relx="0.1",rely="0.8")
    
    
# This will test the number to verify 
# it's an IP that will work
def verifyNum():
    try:
        errorlabel.place_forget()
        key = decompress(fiveDigit.get())
        '''if len(key) != 5: #MUST BE FIVE # Supported @ compression
            raise TypeError
        key = int(key)
        hostname = unencrypt(key)'''
        try:
            global conObject
            
            conObject = Client(key) #key and onDisconnect
            conObject.favdir = favdir
            conObject.PROGCLASS = ProgHandler
            #c.onDisconnect = handleDC
            conObject.start()
            #c.onProgress = updateProgress;
        except Exception as ex:
            pr("Couldn't start client: "+str(ex))
            errorlabel.config(text="The number \""+fiveDigit.get()+"\"\n is not a valid host!")
            errorlabel.place(relx="0.0",rely="0.3")
        else:
            numFrame.place_forget()
            dropLabel.place(relx="0.05",rely="0.27") # PUT THIS THERE WHEN CONNECTED
    except ValueError: #(ValueError,TypeError):
        errorlabel.config(text="The input \""+fiveDigit.get()
                              +"\"\nis not a five digit number.")
        errorlabel.place(relx="0.0",rely="0.3")

submitnum = Tk.Button(numFrame,text="Submit",command=verifyNum)


# Prepare opening screen
buttonFrame = Tk.Frame(frame1,width=PWIDTH-250-75,height=PHEIGHT-150,bg="white")
buttonFrame.place(relx="0.5",rely="0.1")
button1 = Tk.Button(buttonFrame,text="Serve",command=beTheServer,bg="white")
button1.place(relx="0.0",rely="0.02")
button2 = Tk.Button(buttonFrame,text="Client",command=beTheClient,bg="white")
button2.place(relx="0.7",rely="0.02")




# MENUBAR setup and work
menubar = Tk.Menu(top)
filemenu = Tk.Menu(menubar,tearoff=0)
filemenu.add_command(label="History",command=None)

filemenu.add_command(label="About", command=lambda:tkMessageBox.showinfo("About"
                            ,"""Made for the running man \n\n(or woman?)\n\n\n\n\n
            GFileTrade v1.0\n\n\n\n
Because flash drives are stupid!"""))

filemenu.add_separator()
filemenu.add_command(label="Exit", command=top.quit)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = Tk.Menu(menubar,tearoff=0)
'''editmenu.add_command(label="HOLMES",
            command=lambda:str11.set("AYO AYO "+str(mayoVar.get())+str(LB.curselection())))'''
#editmenu.add_radiobutton(label="Radiobutton?",command=None)#Is a bad version of check
editmenu.add_checkbutton(label="Checkbutton?",command=None)
menubar.add_cascade(label="Edit", menu=editmenu)













# Begin mainloop, no code after this part
top.config(menu=menubar)
top.mainloop()