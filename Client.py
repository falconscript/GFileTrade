'''
Created on Dec 10, 2011

@author: 
'''
import socket as S;

import Comm
from Comm import pr as pr
import threading


# Instance created upon choosing to be Client
class Client(threading.Thread,Comm.Comm):
    def __init__(self,hostname):
        threading.Thread.__init__(self)
        self.daemon = True
        Comm.Comm.__init__(self)
        pr("Opening socket...")
        try:
            self.setSock(  S.socket(S.AF_INET,S.SOCK_STREAM)  )
            #self.s.settimeout(6000)
            self.s.connect( ( hostname,4444)  );
        except Exception:
            raise ValueError
    def run(self): #Do not need to call setSock?
        try:
            #self.send_end("Hi&&"+str(S.gethostname())) #+b"\n\0"

            while(True):
                resp = self.recv_end() #1024
                if not resp:
                    break
                
                pr("cReceived message"+str(resp))
                
                if resp == "ENDCONNECTION":
                    pr("Ending client!")
                    break;
                else:
                    self.parseMessage(resp)
            
        except Exception as ex:
            pr("Client Problem DISCONNECTED: "+str(ex))
        finally:
            pr("Closing client socket.");
            self.close()
            
    '''def __del__(self):
        self.s.close()'''
            
    def close(self):
        try:
            self.s.close()
        except (Exception, NameError, AttributeError):
            pass
        try:
            Comm.onDisconnect(True)  #MAY CAUSE INFINITE LOOP
        except (Exception, NameError, AttributeError):
            pass
        
        
# TKDnD reference stuff below, to have out of the way but nearby
"""
top.update()
class CanvasDnd(Tk.Canvas):
    def __init__(self,Master,GiveDropTo, **kw):
        Tk.Canvas.__init__(self,Master,kw)
        self.GiveDropTo = GiveDropTo
    def dnd_accept(self,Source,Event):
        print "Canvas: dnd_accept"
        return self.GiveDropTo
class Receptor:
    '''
    This is a thing to act as a TargetObject
    '''
    def dnd_enter(self,Source,Event):
        '''This is called when the mouse pointer goes from outside the
        Target Widget to inside the Target Widget.
        print "Receptor: dnd_enter"'''
        dropLabel.config(bg="white",text="Yeah! Drop here!")
        
    def dnd_leave(self,Source,Event):
        '''This is called when the mouse pointer goes from inside the
        Target Widget to outside the Target Widget.'''
        print "Receptor: dnd_leave"
        dropLabel.config(bg="light blue",text="Drop Files Here")
        
    def dnd_motion(self,Source,Event):
        '''This is called when the mouse pointer moves withing the TargetWidget.'''
        print "Receptor: dnd_motion"
        
    def dnd_commit(self,Source,Event):
        '''This is called if the DraggedObject is being dropped on us'''
        print "Receptor: dnd_commit; Object received= %s"%`Source`
    def dnd_end(self,Source,Event):
        print "End: ", str(Source) , str(Event)
        
def on_dnd_start(Event):
    '''
    This is invoked by InitiationObject to start the drag and drop process
    '''
    #Create an object to be dragged
    ThingToDrag = TargetObject #Tkdnd.Dragged() 
    #Pass the object to be dragged and the event to Tkdnd
    Tkdnd.dnd_start(ThingToDrag,Event)

'''Object to accept item'''
TargetObject = Receptor()
InitiationObject = Tk.Button(top,text="InitiationObject")
InitiationObject.place(x=0,y=0)
InitiationObject.bind("<ButtonPress>",on_dnd_start,True)


top.update()
top.bind("<<DragEnter>>",lambda Event:pr("DROP!!\n"),True)
top.bind("<<Drag>>",lambda Event:pr("DROP!!\n"),True)
top.bind("<<Drop>>",lambda Event:pr("DROP!!\n"),True)
top.bind("<<DragLeave>>",lambda Event:pr("DROP!!\n"),True)
TargetWidget = CanvasDnd(top,GiveDropTo=TargetObject,relief=Tk.RAISED,bd=2)
#TargetWidget.bind("<<Drop>>", lambda:pr("\nDROP!!\n"), None)
TargetWidget.update()
TargetWidget.bind("<<DragEnter>>",on_dnd_start,True)
TargetWidget.bind("<<Drag>>",lambda Event:pr("DROP!!\n"),True)
TargetWidget.bind("<<Drop>>",lambda Event:pr("DROP!!\n"),True)
TargetWidget.bind("<<DragLeave>>",lambda Event:pr("DROP!!\n"),True)
TargetWidget.place(x=0,y=100)"""
        