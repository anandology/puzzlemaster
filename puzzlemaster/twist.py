"""Twist Puzzle.
"""

import parser
from grid import Grid

class TwistParser:
    def parse(self, lines):
        rows = len(lines)
        cols = len(lines[0])
        
        data = parser.parse_grid(lines)
                
        return Twist(rows, cols, data)

class Twist:
    def __init__(self, rows, cols, data):
        self.rows = rows
        self.cols = cols
        self.data = data
        
    @staticmethod
    def loads(text):
        return TwistParser().parse(text.splitlines())
        
    def render(self):
        grid = Grid(self.cols, self.rows)
        grid.draw_grid(stroke="black", stroke_width=1)
        grid.draw_numbers(self.data)
        return grid.svg


parser.register_puzzle("twist", Twist)

if __name__ == "__main__":
    import doctest
    doctest.testmod()