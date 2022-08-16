#

import math
import random
import turtle
from typing import Tuple

import pandas as pd

DEFAULT_SCREEN = turtle.getscreen()
DEFAULT_TURTLE = DEFAULT_SCREEN.turtles()[0]


class Cluster:

    def __init__(self,
                 speed=5,
                 dot_n=10,
                 circle_r=100,
                 s=DEFAULT_SCREEN,
                 t=DEFAULT_TURTLE
                 ):

        self.s = s
        self.t = t

        self.canv_width = 400
        self.canv_height = 400

        self.t.speed(speed)

        self.dot_r = 5

        self.circle_r = circle_r
        self.circle_line_r = 1

        # generate dots
        _dots = []
        for x in range(dot_n):
            _dots.append({
                "x": random.randint(-1 * self.canv_width, self.canv_width),
                "y": random.randint(-1 * self.canv_height, self.canv_height)
            })
        df = pd.DataFrame(_dots)
        self.dots = self.cw_sort_df(df)

        def quadrant(x, y):
            if x >= 0 and y >= 0:
                return 1
            elif x >= 0 and y < 0:
                return 2
            elif x < 0 and y < 0:
                return 3
            else:
                return 4

        self.dots['q'] = self.dots.apply(lambda row: quadrant(row.x, row.y), axis=1)

    def yield_dots(self, x_offset=0, y_offset=0, pendown=True):

        # copy and sort
        # df = self.cw_sort_df(self.dots.copy())
        df = self.dots.copy()

        # yield dot
        for dot in df.itertuples():
            self.t.penup()
            self.t.goto(dot.x + x_offset, dot.y + y_offset)
            if pendown:
                self.t.pendown()
            yield dot

    def cw_sort_df(self, _df):
        df = _df.copy()
        cw = []

        # get first point, add to list, and get meridian
        cur_dot = df.sort_values(by=['x', 'y']).iloc[0]
        cw.append(cur_dot.name)
        df = df[df.index != cw[0]]

        while len(df) > 0:

            # get all hypot
            df['d'] = df.apply(lambda dot: math.hypot(
                (max([cur_dot.x, dot.x]) - min([cur_dot.x, dot.x])),
                (max([cur_dot.y, dot.y]) - min([cur_dot.y, dot.y]))
            ),
                               axis=1
                               )

            # get first and drop
            cur_dot = df.sort_values(by=['d'], ascending=True).iloc[0]
            cw.append(cur_dot.name)
            df = df[df.index != cur_dot.name]

        _df['cw_sort'] = None
        for order, dot_idx in enumerate(cw):
            _df.loc[dot_idx, 'cw_sort'] = order

        return _df.sort_values(by=['cw_sort'])

    def draw_dots(self):
        self.t.color = 'black'
        for dot in self.yield_dots():
            self.t.dot(self.dot_r)

    def draw_circles(self):
        self.t.color = 'black'
        self.t.pensize(self.circle_line_r)
        for dot in self.yield_dots(y_offset=-1 * self.circle_r):
            self.t.circle(self.circle_r)

    def draw_line(self, s: Tuple[int, int], e: Tuple[int, int], color='red', width=1):
        self.t.penup()
        self.t.goto(*s)
        self.t.pendown()
        self.t.pencolor(color)
        self.t.pensize(width)
        self.t.goto(e)

    def draw_circle_to_circle_BAK(self):
        for i, dot in enumerate(self.dots):
            if i + 1 == len(self.dots):
                return
            self.draw_line(dot, self.dots[i + 1], color='red')

    def draw_outer_path(self):
        last_dot = None
        for i, dot in enumerate(self.yield_dots()):
            if last_dot is None:
                last_dot = dot
                continue
            else:
                self.draw_line((last_dot.x, last_dot.y), (dot.x, dot.y), color='red')
                last_dot = dot
        first_dot = self.cw_sort_df(self.dots.copy()).iloc[0]
        last_dot = self.cw_sort_df(self.dots.copy()).iloc[-1]
        self.draw_line((last_dot.x, last_dot.y), (first_dot.x, first_dot.y), color='red')

    def make(self):
        self.draw_dots()
        self.draw_circles()
        self.draw_outer_path()


if __name__ == "__main__":
    c = Cluster(
        dot_n=100,
        circle_r=10,
        speed=100
    )
    c.make()
    input()
