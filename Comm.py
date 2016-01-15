'''
Created on Dec 13, 2011

@author:

This file is responsible for network communication
and action determination
'''


import time
import os
import select
def pr(s = "No item printed, or null?"):
    pass #print(s)

#CHUNK_SIZE = 8192
CHUNK_SIZE = 32768 #INSANELY fast
#CHUNK_SIZE = 2**10


import urllib2
import socket as S
#import os
from threading import Thread as Thread
import threading

routerflag = None
srOnConnect = None
onDisconnect = None

# Need external verification point
def getExternalIP():
    try:
        return urllib2.urlopen('http://cfalcon.webege.com/ip.php').readlines()[0]
    except Exception as ex2:
        pr("Issue getting External IP" + str(ex2));
        return "Issue getting External IP. Does your router support UPnP?"

# Globals
exip = getExternalIP();
ip = S.gethostbyname(S.gethostname())


lock = threading.Lock()

BUSYFLAG = False


#assume a socket disconnect (data returned is empty string) means  all data was #done being sent.
class Comm():
    ID = 0
    QUEUE = []
    def __init__(self):
        self.progs = {} #A dictionary of progress reports
    def setSock(self,s):
        self.End = "AN END MARKER " + "FOR THE CLASS"
        self.FILE_FINISHED_SENDING_MARKER = "THIS IS THE" + " END OF FILE QUIT NOW HERE"
        self.s = s
        
    # All socket messages pass through this function
    def parseMessage(self,m):
        pr("parsingMessage:"+m)

        if m[:8] == "SENDF1LE": # WE WILL BE RECEVING A FILE.
            self.fileOperation("receive", m[8:])
            
        # Beta feature concept
        if m[:11] == "ReceiveData":
            pass
            #p = self.progs[ int(m[11:12])  ]
            #p.writeChunk( m[12:] )
            
           
    
            
    def fileOperation(self,mode,aFilename):
        global BUSYFLAG
        filename = None
        
        if mode == "send":
            filename = str(os.path.basename(aFilename)) + str(Comm.ID)
            Comm.ID+=1
            self.progs[filename] = self.PROGCLASS(str(os.path.basename(aFilename))
                                          ,int(os.path.getsize(aFilename))," sent")
            
            self.progs[filename].start()
            
        # Maintain through flags no threading issues.
        # Mutexes/Locks/Conditions failed me here. Innovated Queue style.
        Comm.QUEUE.append(filename)
        #flagCounter = 0;
        while BUSYFLAG :#or flagCounter < 3 :
            time.sleep(0.1)
            if not BUSYFLAG and Comm.QUEUE[0] == filename:
                break
            
        BUSYFLAG = True
        Comm.QUEUE.pop(0); # Remove this item from Queue!
                
        
        if mode == "receive":
            #self.send_end("OKAY!")
            pr("RECEIVING FILE NOW")
            
            fileinfo = aFilename.split(":[]")
            
            pr("GotFileInfo: "+ str(fileinfo))
            sizeofFile = fileinfo[0]
            filename = fileinfo[1] #SINGLE FILENAME
            
            # PREPARE FILENAME to save to
            if len(self.favdir.get() ):
                if self.favdir.get()[-1] != os.sep:
                    filename = self.favdir.get() +os.sep+ filename
                else: 
                    filename = self.favdir.get() + filename
            
            # TODO: POSSIBLY CHECK IF DIRECTORY. Mac allows goofy things
            
            # Add 0's to filename if a file by this name already exists
            while os.path.isfile(filename):
                ext = os.path.splitext(filename)[1]
                filename = filename[:filename.rfind(ext)] 
                filename = filename + "0"+ ext
            pr("SAVING FILE AS: "+filename)
            
            
            # Init proghandler
            self.progs[filename] = self.PROGCLASS(
                                    os.path.basename(filename),int(sizeofFile)," received")
            self.progs[filename].start()
            
            # Open file, read then send chunk, and update its progress handler
            try:
                fhandle = open(filename, "wb")
                
                totalBytesSent = 0
                while True:
                    chunk = self.recv_end()
                    if chunk == self.FILE_FINISHED_SENDING_MARKER:
                        break;
                    else:
                        fhandle.write( chunk )
                        fhandle.flush()
                        totalBytesSent += len(chunk)
                        self.progs[filename].onProgress( totalBytesSent )
                    
                
                self.progs[filename].onFinish(); self.progs.pop(filename)
                fhandle.close()
                '''lock.release()'''
                BUSYFLAG = False
                pr("FILE WRITTEN AND ENTIRELY RECEIVED!")
            except Exception as ex:
                pr("Problem during RECEIVE/WRITE:"+str(ex))

                self.progs[filename].onFailure();  self.progs.pop(filename)
                '''lock.release()'''
                BUSYFLAG = False
                raise ValueError
            
        if mode == "send":

            # THIS IS CURRENTLY HANDLED BEFORE MODECHECKING. In Next version, change?
            '''filename = str(os.path.basename(aFilename)) + str(Comm.ID)
            Comm.ID+=1
            self.progs[filename] = self.PROGCLASS(filename
                                          ,int(os.path.getsize(aFilename))," sent")
            self.progs[filename].start()'''
            
        
            pr("Going to send file: "+aFilename)
            self.send_end("SENDF1LE"
                + str(os.path.getsize(aFilename))+":[]"+os.path.basename(aFilename) )

            try:
                pr("About to open: "+aFilename)
                
                #lock.acquire() #Threading mutex
                fhandle = open(aFilename,"rb+") # Always BINARY
                
                totalBytesSent = 0
                while True:
                    packet = fhandle.read(CHUNK_SIZE)
                    if packet == '':
                        break
                    self.send_end( packet )
                    totalBytesSent += len(packet)
                    self.progs[filename].onProgress(totalBytesSent)
                    if len(packet) < CHUNK_SIZE: break;
                self.send_end(self.FILE_FINISHED_SENDING_MARKER) #MANUAL END SEND
                self.progs[filename].onFinish(); self.progs.pop(filename)
                    
                        
                fhandle.close() 
                '''lock.release() #Threading mutex'''
                BUSYFLAG = False
            except Exception as ex:
                self.progs[filename].onFailure(); self.progs.pop(filename)
                pr("Exception while opening/sending file: "+str(ex));
                fhandle.close() #Do this code ALWAYS
                '''lock.release() #Threading mutex'''
                BUSYFLAG = False
                raise ValueError
                    
    """def prepToSend(self,aFilename):
        '''res = self.recv_end() #REALLY OBNOXIOUS APPARENTLY IS NOT NEEDED
        pr("Should be 'OKAY!': "+res)
        if res != "OKAY!" :
            pr("Wasn't OKAY! res is "+str(res))
            return False'''
        return True
    '''def __del__(self):
        self.s.close()'''"""
                    
                    

    '''
    Python's default socket library is reaaaaally bad!
    You need to have both the size of the data before it is sent,
    AND handle TCP fragmentation manually. I solve these problems with
    predetermined packet sizes (basically software defined MTU) and
    delimiters determining end of file 
    '''
    def recv_end(self):
        while(True): # Check for new messages
            pr("In recv_end loop")
            
            if select.select([self.s],[],[])[0]:
                pr("after select! waiting for sizeOfMessage...")
                total_data =[]; #actualMessage = ''
                while True : # SEND WHOLE MESSAGE
                    actualMessage = ''
                    sizeOfMessage = ''
                    while len(sizeOfMessage) != 24:
                        if select.select([self.s],[],[])[0]:
                            sizeOfMessage += self.s.recv(24-len(sizeOfMessage))
                    #pr("sizeOfMessage received WAS: "+sizeOfMessage)
                    
                    while  len(actualMessage) < int(sizeOfMessage) :
                        if select.select([self.s],[],[])[0]:
                            actualMessage += self.s.recv(int(sizeOfMessage)-len(actualMessage))
                            #pr("Made a read for the greater message");

                    #pr("TRUESIZE: " + str(len(actualMessage)));
                    
                    if self.End in actualMessage:
                        '''FULL MESSAGE RECEIVED'''
                        total_data.append(actualMessage[:actualMessage.find(self.End)])
                        
                        return ''.join(total_data)
                    else: 
                        total_data.append( actualMessage )
                    #pr("actualMessage received WAS: "+actualMessage)
 
        
    '''
    As mentioned above send_recv, Python's socket libraries
    leave many problems. These two functions are the best
    tools for sending network messages. Python's Twisted library
    would probably be better in a production environment
    '''
    def send_end(self,data):
        while len(data) > CHUNK_SIZE:
            chunk = data[:CHUNK_SIZE]
            sizeOfMessage = str(len(chunk))

            while len(sizeOfMessage) < 24:
                sizeOfMessage = "0"+sizeOfMessage
            self.s.sendall(   sizeOfMessage    )   #;self.s.flush()
            #pr("Sending message of size:"+ sizeOfMessage) #+"\nActualMessage: "+chunk)
            self.s.sendall(chunk) #;self.s.flush()
            #pr("ACTUALLY SENT MESSAGE")
            data = data[CHUNK_SIZE:]
            
        finalMessage = data + self.End;
        sizeOfFinalMessage = str(len(finalMessage))
        
        while len(sizeOfFinalMessage) < 24:
            sizeOfFinalMessage = "0"+sizeOfFinalMessage
            
        self.s.sendall(   sizeOfFinalMessage   ) #;self.s.flush()
        
        #pr("Sending message of size:"+ str(len(finalMessage))+"\nActualMessage: "+finalMessage)
        
        self.s.sendall(finalMessage)  #;self.s.flush()
        
        
        
