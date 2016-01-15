'''
Created on Dec 10, 2011

@author:
'''

import socket as S
import threading
import Comm
import time
from Comm import pr


    
# Class is instantiated upon determining server mode
class Serve(threading.Thread,Comm.Comm):
    def __init__(self,):
        threading.Thread.__init__(self)
        self.daemon = True
        Comm.Comm.__init__(self)
        self.exitflag = False
        pr("Starting server...");
        try:
            self.serv = S.socket(S.AF_INET,S.SOCK_STREAM)
            
            #self.serv.settimeout(6000)
            self.serv.setsockopt(S.SOL_SOCKET, S.SO_REUSEADDR, 1)
            #pr("Hosting at: "+S.gethostbyname(S.gethostname()))
            
            if S.gethostbyname(S.gethostname()) != Comm.exip:
                Comm.routerflag = True
            #else: # Do always I guess. In future add UDP Punchthrough support
            #Comm.routerflag = False
            pr("Hosting at:" + str(  S.gethostbyname(S.gethostname()) ));
            self.serv.bind((  S.gethostbyname(S.gethostname())  ,4444))
            self.serv.listen(1) #Just one at a time
        except (Exception,AttributeError):
            raise ValueError
        
        
    def run(self):
        try:
            #normally we'd maybe make a new thread here
            self.serv.setblocking(False)
            while True:
                try:
                    if self.exitflag:
                        self.serv.close()
                        return
                    c, addr = self.serv.accept() #Throws exception if no client

                    break
                except Exception as ex:
                    pass
                    time.sleep(0.01)

            self.setSock(  c  )
            self.s.setblocking(True) #Hmm no difference?
            pr("Received connection from: " + str(addr))
            Comm.srOnConnect()
            
            pr("Entering message watch loop")
            while ( True ) :
                pr("Server waiting for message...")
                resp = self.recv_end() #1024
                if not resp:
                    break
                elif resp == "ENDCONNECTION":
                    pr("Closing Client: " + str(self.s))
                    self.s.close()
                    break
                else:
                    self.parseMessage(resp)
                    pr("sGotMessage: " + str(resp))
                    #c.send("Got you: " +resp)
            
        except Exception as ex:
            pr("Serve Problem: " + str(ex))
            #self.close()

        finally:
            pr("Ended Server.")
            self.close()
    def close(self):
        try:
            self.exitflag = True
            self.s.close()
        except (Exception, NameError, AttributeError):
            pass
        
        try:
            pr("Closing server...")
            self.serv.close()
            pr("Server closed.")
        except (Exception, NameError, AttributeError):
            pass
        
        try:
            Comm.onDisconnect(True) # Was worried about infinite loop here
        except (Exception, NameError, AttributeError):
            pass
