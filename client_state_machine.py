"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import ball_game

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.ball = ''
        self.gameuser = 0
        self.ball_color = 'red'

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''
        
    ############GAME#################
    def game_to(self, peer):
        msg = json.dumps({"action": "game", 'status': 'request', "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.out_msg += 'You are connected with '+ peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        elif response['status'] == 'deny':
            self.out_msg += 'Peer denied your request\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)
    ############GAME#################

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                #############---game---###################
                elif my_msg[0] == 'g':
                    peer = my_msg[1:].split()[0]
                    peer = peer.strip()
                    if len(my_msg[1:].split()) > 1:
                        self.ball_color = my_msg[1:].split()[1].lower()
                    if self.game_to(peer) == True:
                        self.state = S_GAME
                        self.peer = peer
                        self.out_msg += 'Connect to ' + peer + '. Play Game!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        self.out_msg += 'you are player 2, control the right board\n'
                        self.gameuser = 2
                        self.ball = ball_game.Ball(ball_game.setup(), self.ball_color)
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                #############---game---###################

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg.get("action", '') == "connect":

                    # ----------your code here------#
                    if peer_msg['status'] == "request":
                        self.state = S_CHATTING
                        self.out_msg += 'You are connected with {}\n'.format(peer_msg['from'])
                        self.out_msg += '-----------------------------------\n'
                    # ----------end of your code----#
###########################################game######################
                if peer_msg.get("action", '') == 'game':
                    self.out_msg += peer_msg['from'] + ' want to play game with you. Type [y_ball color] to accept, [n] to deny'
                    self.peer = peer_msg['from']
                    self.state = S_CONFIRMING
                    
                        
        elif self.state == S_CONFIRMING:
            if len(my_msg) > 0:
                if my_msg[0] == 'n':
                    mysend(self.s, json.dumps({'action': 'game', 'status': 'deny', 'peer': self.peer}))
                    self.state = S_LOGGEDIN
                elif my_msg[0] == 'y':
                    self.state = S_GAME
                    self.out_msg += 'You are connected with '+ self.peer + '\n'
                    self.out_msg += '-----------------------------------\n'
                    self.out_msg += 'you are player 1, control the left board\n'
                    self.gameuser = 1
                    if len(my_msg.strip()) > 1:
                        self.ball_color = my_msg[1:].strip().lower()
                    self.ball = ball_game.Ball(ball_game.setup(), self.ball_color)
                    mysend(self.s, json.dumps({'action': 'game', 'status': 'accept', 'peer': self.peer}))
                
                
        elif self.state == S_GAME:
            
            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
                
                if peer_msg['action'] == 'move' :
                    step = peer_msg['step']
            
            else:
                step = 0
                
            self.ball.update_canvas()
            if self.gameuser == 1:
                self.ball.update(0, step)
                if my_msg == 'w':
                    self.ball.update(30, 0)
                    mysend(self.s, json.dumps({'action': 'move', 'step': 30, 'peer': self.peer}))
                elif my_msg == 's':
                    self.ball.update(-30, 0)
                    mysend(self.s, json.dumps({'action': 'move', 'step': -30, 'peer': self.peer}))
            elif self.gameuser == 2:
                self.ball.update(step, 0)
                if my_msg == 'w':
                    self.ball.update(0, 30)
                    mysend(self.s, json.dumps({'action': 'move', 'step': 30, 'peer': self.peer}))
                elif my_msg == 's':
                    self.ball.update(0, -30)
                    mysend(self.s, json.dumps({'action': 'move', 'step': -30, 'peer': self.peer}))
            
            lose, loser = self.ball.who_lose()
            if lose:
                if self.gameuser == loser:
                    self.out_msg += "you lose\n"
                else:
                    self.out_msg += self.peer + ' lose\n'
                self.state = S_LOGGEDIN
                
                
################################################game######################   
                    
                
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
  

                # ----------your code here------#
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
                
                if peer_msg['action'] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg += peer_msg['msg'] + '\n'
                if peer_msg['action'] == 'exchange':
                    self.out_msg += peer_msg['from'] + ": " + peer_msg['message']
                # ----------end of your code----#

                
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
