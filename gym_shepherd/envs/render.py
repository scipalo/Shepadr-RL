from scipy.spatial import distance
from math import sqrt
import tkinter as tk
from tkinter import *
import reward
import time

"""
# parametri
herd = [(13, 10), (6, 14), (14, 1), (2, 7), (15, 16), (9, 5), (12, 12), (1, 8), (7, 19), (8, 2)]
dog = (5,5)
goal_radius = 1
field_size = 20
dog_impact = 5 #razdalja pri kateri pes vpliva na ovce
"""

# RISANJE

# pripravimo površino za risanje

def drawing_init(field_size):
    master = Tk()
    rows=field_size
    columns=field_size
    size=30     #velikost kvadratka
    color1="lightgreen" 
    color4="green"
    canvas_width = columns * size
    canvas_height = rows * size
    canvas = tk.Canvas(borderwidth=0, highlightthickness=0,
                                    width=canvas_width, height=canvas_height, background="lightgreen")
    #canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)
    canvas.pack()


    # Narišemo kvadratke
    for row in range(rows):
        for col in range(columns):
            x1 = (col * size)
            y1 = (row * size)
            x2 = x1 + size
            y2 = y1 + size
            canvas.create_rectangle(x1, y1, x2, y2, outline=color4, fill=color1, tags="square")


def draw(herd, dog, canvas, size=30):
    #pobrišemo ovce in psa iz prejšnjega koraka
    #canvas.delete("sheep")
    #canvas.delete("dog")
#narišemo ovce
    color2 = "yellow"
    color3 = "brown"

    for sheep in herd:
        x1 = (sheep[0] *  size) 
        y1 = (sheep[1] *  size)
        x2 = x1 +  size
        y2 = y1 +  size
        canvas.create_oval(x1, y1, x2, y2, outline= color2, fill= color2, tags="sheep")
#narišemo center ovc
    c, seznam = dist_herd_center(herd)
    x1 = (c[0] *  size) 
    y1 = (c[1] *  size)
    x2 = x1 +  size
    y2 = y1 +  size
    canvas.create_oval(x1, y1, x2, y2, outline= color2, fill= "black", tags="sheep")
#narišemo psa
    x1 = ( dog[0] *  size) 
    y1 = ( dog[1] *  size)
    x2 = x1 +  size
    y2 = y1 +  size
    canvas.create_oval(x1, y1, x2, y2, outline= color3, fill= color3, tags="dog")

    # narišemo črte, da je lažje gledati koliko ovc je v katerem območju
    # canvas.create_line( dog[0]*  size+  size/2,  dog[1]*  size+  size/2,  dog[0]*  size+10 *  size,  dog[1]*  size+10*  size)

    # canvas.create_line( dog[0]*  size+  size/2,  dog[1]*  size+  size/2,  dog[0]*  size-10 *  size,  dog[1]*  size-10*  size)

    # canvas.create_line( dog[0]*  size+  size/2,  dog[1]*  size+  size/2,  dog[0]*  size+10 *  size+  size/2,  dog[1]*  size-10*  size+  size/2)

    # canvas.create_line( dog[0]*  size+  size/2,  dog[1]*  size+  size/2,  dog[0]*  size-10 *  size+  size/2,  dog[1]*  size+10*  size+  size/2)


# risanje
# draw(herd,dog)
# mainloop()