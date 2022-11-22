"""Loop Puzzle.
"""

from . import parser
from .grid import Grid

class LoopParser:
    def parse(self, lines):
        rows = len(lines)/2
        cols = len(lines[0])/2

        grid = parser.parse_grid(lines)
        hlines = [(x/2, y/2) for y, x in grid if grid[y, x] in "_-"]
        vlines = [(x/2, y/2) for y, x in grid if grid[y, x] == "|"]

        return Loop(rows, cols, hlines, vlines)

class Loop:
    def __init__(self, rows, cols, hlines, vlines):
        self.rows = rows
        self.cols = cols
        self.hlines = hlines
        self.vlines = vlines

    @staticmethod
    def loads(text):
        return LoopParser().parse(text.splitlines())

    def render(self):
        grid = Grid(self.cols, self.rows)
        grid.draw_corners(r=6)
        grid.draw_grid(stroke_dasharray="4 4", stroke="black", stroke_width=1)

        for x, y in self.hlines:
            grid.hline(x, y, 1, stroke="black", stroke_width=4)

        for x, y in self.vlines:
            grid.vline(x, y, 1, stroke="black", stroke_width=4)

        return grid.svg

parser.register_puzzle("loop", Loop)