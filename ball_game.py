#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 16:58:37 2019

@author: apple
"""
from tkinter import *
import random
import time
 

 
class Ball:
    #创建一个球类
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
        #返回刚好划小球的id，create_oval创建一个椭圆
        self.canvas.move(self.id, 245, 100)
        #把椭圆移动到画布
        #starts = [-3, -2, -1, 1, 2, 3]
        #random.shuffle(starts)
        #随机排列
        self.x = -3
        self.y = -3
        self.canvas_height = self.canvas.winfo_height()
        #获取画布当前高度
        self.canvas_width = self.canvas.winfo_width()
        #获取画布当前宽度
        
        self.id_left = canvas.create_rectangle(0, 100, 10, 250, fill = "purple")
        #get rectangle left position
        self.id_right = canvas.create_rectangle(self.canvas_width - 10, 100, self.canvas_width, 250, fill = "purple")
    def draw(self):
        self.canvas.move(self.id, self.x, self.y)
        #让小球水平和垂直移动
        pos = self.canvas.coords(self.id)
        #get ball
        
        pos_left = self.canvas.coords(self.id_left)
        #get left coords
        pos_right = self.canvas.coords(self.id_right)
        #get right coords
 
        #判断小球是否撞到画布顶部或者底部，保证小球反弹回去，不消失
        if pos[1] <= 0:
            self.y = 3
        if pos[3] >= self.canvas_height:
            self.y = -3
        if pos[0] <= 0 and pos[1] <= pos_left[3] and pos[1] >= pos_left[1]:
            self.x = 3
        if pos[2] >= self.canvas_width and pos[1] <= pos_right[3] and pos[1] >= pos_right[1]:
            self.x = -3
            
    def update_left(self, up_left = 0):
        self.canvas.move(self.id_left,0 ,-up_left )
        
    def update_right(self, up_right = 0):
        self.canvas.move(self.id_right,0 ,-up_right )
        
    def update_canvas(self):
        self.draw()
        tk.update_idletasks()
        tk.update()
        time.sleep(0.01)
        
    def update(self, up_left, up_right): 
        self.update_left(up_left)
        self.update_right(up_right)
    
    def who_lose(self):
        pos = self.canvas.coords(self.id)
        if pos[0] <= -5:
            tk.destroy()
            return True, 1
        elif pos[2] >= self.canvas_width + 5:
            tk.destroy()
            return True, 2
        else:
            return False, 0
        
        

def setup():

    global tk
    
    tk = Tk()
    tk.title("Game")
     
    tk.resizable(0, 0)
    #窗口大小不可调整
    tk.wm_attributes("-topmost", 1)
    #使画布窗口置于所有窗口之前
    canvas = Canvas(tk,width=500, height=400, bd=0, highlightthickness=0)
    #bd和highlighttthickness是为了保证画布没有边框
    canvas.pack()
    tk.update()
    return canvas

"""
        if msvcrt.kbhit(): 
            key = ord(msvcrt.getch())
            if key == ord("w"):
                up_left = 30
            elif key == ord("s"):
                up_left = -30
            elif key == ord("i"):
                up_right = 30
            elif key == ord("k"):
                up_right = -30
            else:
                up_left = 0
                up_right = 0
        else:
            up_left = 0
            up_right = 0
        update(up_left, up_right)
"""
