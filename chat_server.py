"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
#encryption
from Crypto.Hash import SHA256


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.users = {}
 

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)
        
    def register(self, sock, msg):
        name = msg["name"]
        if name in self.users:
            mysend(sock,json.dumps({"server_response":"Name has been used"}))
        else:
            password = msg["password"]
            #hash
            self.users[name] = SHA256.new((password).encode('utf-8')).hexdigest()
            self.indices[name] = indexer.Index(name)
            print(name + ' has registered')
            mysend(sock, json.dumps({"server_response":"register_succeed"}))
        
        
    def login(self, sock, msg):
        # read the msg that should have login code plus username
                
        name = msg["name"]
        password =SHA256.new((msg["password"]).encode('utf-8')).hexdigest()
        if name in self.users:
            if password == self.users[name]:
                mysend(sock, json.dumps({"server_response":"login succeed"}))
                status = S_LOGGEDIN
            
            else:
                mysend(sock, json.dumps({"server_response":"wrong password"}))
                return None
        else:
       
            mysend(sock,json.dumps({"server_response":'fail'}))
            return None
                                
                                
        if status == S_LOGGEDIN:
                    # move socket from new clients list to logged clients
                    #   if self.group.is_member(name) != True:
            self.new_clients.remove(sock)
                    # add into the name to sock mapping
            self.logged_name2sock[name] = sock
            self.logged_sock2name[sock] = name
            print(name + ' has logged in')
            self.group.join(name)
                    # load chat history of that user
            if name not in self.indices.keys():
                try:
                    self.indices[name] = pkl.load(
                    open(name + '.idx', 'rb'))
                except IOError:  # chat index does not exist, then create one
                    self.indices[name] = indexer.Index(name)
            
            else:
                mysend(sock, json.dumps({"server_response": 'fail'}))
        
        
        


    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            
            
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
# ==============================================================================
# handle messeage exchange: IMPLEMENT THIS
# ==============================================================================
            elif msg['action'] == 'register':
                name = msg['name']
                password = msg['password']
                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    
                if name not in self.users:
                    self.users[name] = password
                    mysend(to_sock, json.dumps({'server_response': 'register_succeed'}))
                    
                else:
                    mysend(to_sock, json.dumps({'server_response': 'register_unsucceed'}))
                    
                    
            elif msg['action'] == 'login':
                name = msg['name']
                password = msg['password']
                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    
                if name in self.users:
                    if self.users[name] == password:
                        mysend(to_sock, json.dumps({'server_response': 'login succeed'}))
                    else:
                        mysend(to_sock, json.dumps({'server_response': 'wrong password'}))
                else:
                    mysend(to_sock, json.dumps({'server_response': 'login'}))
            
#############################################GAME#####################################
            elif msg['action'] == 'game':
                if msg['status'] == 'request':
                    to_name = msg["target"]
                    from_name = self.logged_sock2name[from_sock]
                    if to_name == from_name:
                        to_sock = self.logged_name2sock[to_name]
                        msg = json.dumps({"action": "game", "status": "self"})
                    # connect to peer
                    else:
                        to_sock = self.logged_name2sock[to_name]
                        mysend(to_sock, json.dumps(
                                {'action': 'game', 'from': from_name}))
                elif msg['status'] == 'accept':
                    to_name = msg['peer']
                    to_sock = self.logged_name2sock[to_name]
                    mysend(to_sock, json.dumps(
                                {'action': 'game', 'status': 'success'}))
                elif msg['status'] == 'deny':
                    to_name = msg['peer']
                    to_sock = self.logged_name2sock[to_name]
                    mysend(to_sock, json.dumps(
                                {'action': 'game', 'status': 'deny'}))
                    
            elif msg['action'] == 'move':
                to_name = msg["peer"]
                to_sock = self.logged_name2sock[to_name]
                mysend(to_sock, json.dumps({"action": "move", "step": msg['step']}))
                    
#############################################GAME#####################################
            
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                m = msg['message']
                ctime = time.strftime('%m.%y,%H:%M', time.localtime())
                message_add = '[' + ctime + ']' + m
                self.indices[from_name].add_msg_and_index(m)

                # ---- end of your code --- #

                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]

                    # IMPLEMENTATION
                    # ---- start your code ---- #
                    
                    mysend(to_sock, json.dumps(
                                {"action": "exchange", "from": from_name, "message": message_add}))

                    # ---- end of your code --- #

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "msg": "everyone left, you are alone"}))
# ==============================================================================
#                 listing available peers: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #
                msg = str(self.group.list_all(''))

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                num = int(msg["target"])
                poem = ''
                content = self.sonnet.get_poem(num)
                for i in content:
                    poem += i + '\n'
                    
                    

                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search: : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #
                from_name = self.logged_sock2name[from_sock]
                search_rslt = ''
                try:
                    for sentence in self.indices:
                        search_rslt += '(' + str(sentence) + ')' + str(self.indices[sentence].search(msg["target"])) + '\n'
                except:
                    search_rslt = ''
                    

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))

# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                
                    msg = json.loads(myrecv(newc))
                    action = msg['action']
                    if action == "register":
                        self.register(newc,msg)
                    elif action == "login":
                        self.login(newc,msg)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
