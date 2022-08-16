
import random

import turtle

DEFAULT_SCREEN = turtle.getscreen()
DEFAULT_TURTLE = DEFAULT_SCREEN.turtles()[0]

_s = DEFAULT_SCREEN
_t = DEFAULT_TURTLE


def square(l, t:turtle.Turtle = None):

    if t is None:
        t = _t

    for x in range(4):
        t.forward(l)
        t.left(90)

def rand_coord(x=400, y=400):
    return random.randint(-1 * x, x), random.randint(-1 * y, y)


def foo(dot_n=10, circle_r=100):

    t = DEFAULT_TURTLE

    # generate dot locations
    dot_locs = []
    for x in range(dot_n):
        dot_locs.append(rand_coord())

    # draw dots
    for dot_loc in dot_locs:
        t.penup()
        t.goto(*dot_loc)
        t.color('black')
        t.dot(5)

    # draw circles
    for dot_x, dot_y in dot_locs:
        t.penup()
        t.goto(dot_x, dot_y - circle_r)
        t.width(2)
        t.pendown()
        t.circle(circle_r)














