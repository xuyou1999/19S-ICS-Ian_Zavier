import time
import socket
import select
import sys
import json
from chat_utils import *
import client_state_machine as csm
from tkinter.dialog import *
from tkinter import *
import tkinter as tk

import threading

from tkinter import *
from tkinter.dialog import *

class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.user = {}

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        #peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
           
        def log_in():
            global con1
            con1 = e1.get()
            con2 = e2.get()
            len1 = len(con1)
            len2 = len(con2)
            
            mysend(self.socket,json.dumps({"action":"login","name":con1,"password":con2}))          
            response = json.loads(self.recv())
            
            if response["server_response"] == "login succeed":
                c['text'] = 'You successfully logged in!'
                
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(con1)
                self.print_instructions()

                return True
                
            elif response["server_response"] == 'wrong password':
                c['text'] = 'The password is wrong. Please try again'
            
            else:
                c['text'] = 'Please register first'
                
                
            

            e1.delete(0, len1)
            e2.delete(0, len2)
    
        def register():
    
            root2 = tk.Tk()
            root2.geometry('450x200')
            root2.title('Register Page')
    
            def confirm():
                con1 = e1.get()
                con2 = e2.get()
                con3 = e3.get()
                len1 = len(con1)
                len2 = len(con2)
                len3 = len(con3)
                if con2 == con3:
                    
                    mysend(self.socket,json.dumps({"action":"register","name":con1,"password":con2}))          
                    response = json.loads(self.recv())
                    if response["server_response"] == "register_succeed":
          
                        c['text'] = 'successfully registered! '
                        root2.destroy()
                    else:
                        f['text'] = 'user name has been used'
                        
                else:
                    f['text'] = 'Two passwords are not the same. \nPlease try again!'
        
                
                    e1.delete(0, len1)
                    e2.delete(0, len2)
                    e3.delete(0, len3)
        
            
            c['text'] = ''
            
            b1 = Label(root2, text='User name:                                ')
            b1.grid(row=0, column=0, sticky=W)
            
            e1 = Entry(root2)
            e1.grid(row=0, column=1, sticky=E)
            
            b2 = Label(root2, text='password:                                 ')
            b2.grid(row=1, column=0, sticky=W)
            
            e2 = Entry(root2)
            e2['show'] = '*'
            e2.grid(row=1, column=1, sticky=E)
            
            b3 = Label(root2, text='password again:                             ')
            b3.grid(row=2, column=0, sticky=W)
            
            e3 = Entry(root2)
            e3['show'] = '*'
            e3.grid(row=2, column=1, sticky=E)
            
            d = Button(root2, text='确认', command=confirm)
            d.grid(row=3, column=1, sticky=E)
            
            f = Label(root2, text='')
            f.grid(row=3)
            


    
 
        global f
        global c
        

        
        root = tk.Tk()
        root.geometry('400x200')
        root.title('Log in Page')
        
        b1 = Label(root, text='User name:                            ')
        b1.grid(row=0, column=0, sticky=W)
        
        e1 = Entry(root)
        e1.grid(row=0, column=1, sticky=E)
        
        b2 = Label(root, text='Password:                            ')
        b2.grid(row=1, column=0, sticky=W)
        
        e2 = Entry(root)
        e2['show'] = '*'
        e2.grid(row=1, column=1, sticky=E)
        
        c = Label(root, text='')
        c.grid(row=3)
        
        b = Button(root, text='Register', command=register)
        b.grid(row=2, column=1, sticky=W)
                
        d = Button(root, text='Log in', command=log_in)
        d.grid(row=2, column=1, sticky=E)
        
        root.mainloop()
        
        

        

    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text) # no need for lock, append is thread safe

    def print_instructions(self):
        self.system_msg += menu
        
    

    def run_chat(self):
        self.init_chat()
        self.login()
        
        if self.state == S_LOGGEDIN:
            self.system_msg += 'Welcome, ' + con1 + '!'
            self.output()
            while self.sm.state != S_OFFLINE:
                self.proc()
                self.output()
                time.sleep(CHAT_WAIT)
            self.quit()


        
       

#==============================================================================
# main processing loop
#==============================================================================
    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
        
        