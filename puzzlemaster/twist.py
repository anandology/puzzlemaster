"""Twist Puzzle.
"""

import re
from . import parser, utils
from .grid import Grid
import pprint

class TwistParser:
    """Twist puzzle parser.

    Sample:

        1223
        3114
        4212
        3434
    """
    def parse(self, lines):
        rows = len(lines)
        cols = len(lines[0])

        data = parser.parse_grid(lines)

        return Twist(rows, cols, data)

class TwistSolutionParser:
    """Twist solution parser.

    Sample:

        >>> p = TwistSolutionParser()
    """
    def parse(self, lines):
        data = parser.parse_grid(lines)

        m = utils.dict2matrix(data)
        d = [row[::2] for row in m[::2]]

        twist = Twist(len(d), len(d[0]), utils.matrix2dict(d))
        markers = {
            "|": [0, -1, 0, 1],
            "-": [-1, 0, 1, 0],
            "\\": [-1, -1, 1, 1],
            "/": [1, -1, -1, 1]
        }

        connections = []
        for (y, x), v in sorted(data.items()):
            if v in markers:
                dx1, dy1, dx2, dy2 = markers[v]
                x1, y1 = (x+dx1)/2, (y+dy1)/2
                x2, y2 = (x+dx2)/2, (y+dy2)/2
                c = (y1, x1), (y2, x2)
                connections.append(c)

        return TwistSolution(twist, connections)

class Twist:
    def __init__(self, rows, cols, data):
        self.rows = rows
        self.cols = cols
        self.data = data

    @staticmethod
    def loads(text):
        return TwistParser().parse(text.splitlines())

    def render(self):
        grid = self.render_grid()
        return grid.svg

    def render_grid(self):
        grid = Grid(self.cols, self.rows)

        grid.rect(0, 0, 1, 1, fill="#ddd")
        grid.rect(self.cols-1, self.rows-1, 1, 1, fill="#ddd")

        grid.draw_grid(stroke="black", stroke_width=2)
        grid.draw_numbers(self.data)
        return grid

    def solve(self):
        return TwistSolver(self.data).solve()

    def tostring(self):
        return utils.matrix2str(utils.dict2matrix(self.data))

    def __str__(self):
        return "puzzle: twist\n\n" + self.tostring()

class TwistSolution:
    def __init__(self, twist, connections):
        self.puzzle = twist
        self.connections = connections

    @staticmethod
    def loads(text):
        return TwistSolutionParser().parse(text.splitlines())

    def render(self):
        grid = self.puzzle.render_grid()
        for (y1, x1), (y2, x2) in self.connections:
            # we want to draw from the centers
            x1, y1, x2, y2 = x1+0.5, y1+0.5, x2+0.5, y2+0.5

            # Start from some offset to avoid writing on the letters
            dx = (x2-x1) * 0.2
            dy = (y2-y1) * 0.2
            x1, y1, x2, y2 = x1+dx, y1+dy, x2-dx, y2-dy

            grid.line(x1, y1, x2, y2, stroke="black", stroke_width=4)
        return grid.svg

    def tostring(self):
        d = dict(
                ((2*r, 2*c), v)
                for ((r, c), v) in self.puzzle.data.items())

        for (y1, x1), (y2, x2) in self.connections:
            dy = y2-y1
            dx = x2-x1

            if dx == 0:
                d[y1+y2, x1+x2] = "|"
            elif dy == 0:
                d[y1+y2, x1+x2] = "-"
            elif dx + dy == 0:
                d[y1+y2, x1+x2] = "/"
            else:
                d[y1+y2, x1+x2] = "\\"

        return utils.matrix2str(utils.dict2matrix(d))

    def __str__(self):
        return "puzzle: twist-solution\n\n" + self.tostring()

class TwistGenerator:
    def __init__(self, rows, cols, max):
        self.rows = rows
        self.cols = cols
        self.max = max

    def generate(self):
        data = []

def cross(A, B):
    return ((a, b) for a in A for b in B)

class TwistSolver:
    """Twist Puzzle solver.

        >>> s = TwistSolver([[1, 2], [1, 2], [1, 2]])
        >>> s.rows
        [0, 1, 2]
        >>> s.cols
        [0, 1]
        >>> s.values = [1, 2]
        >>> s.next_value[1]
        2
        >>> s.next_value[2]
        1
        >>> s.graph
    """
    def __init__(self, data):
        if isinstance(data, list):
            data = utils.matrix2dict(data)
        self.data = data
        self.rows = len(set(r for r, c in data))
        self.cols = len(set(c for r, c in data))
        self.values = sorted(set(data.values()))

        self.begin = (0, 0)
        self.end = (self.rows-1, self.cols-1)

        self.next_value = dict(zip(self.values, self.values[1:] + self.values[:1]))

        self.grid = data
        self.graph = dict((rc, self.get_next(*rc)) for rc in self.grid)

    def get_next(self, r, c):
        next = self.next_value[self.grid[r, c]]
        return [n for n in cross([r-1, r, r+1], [c-1, c, c+1]) if self.grid.get(n) == next]

    def make_connections(self, nodelist):
        return zip(nodelist, nodelist[1:])

    def solve(self):
        for s in self._solve(self.graph, {}, self.begin):
            nodes = [item[0] for item in sorted(s.items(), key=lambda item: item[1])]
            connections = zip(nodes, nodes[1:])
            yield TwistSolution(Twist(self.rows, self.cols, self.data), connections)

    def solve_one(self):
        s = self.solve()
        try:
            return s.next()
        except StopIteration:
            return None

    def are_crossing(self, a, b, visited):
        y1, x1 = a
        y2, x2 = b

        p = y2, x1
        q = y1, x2

        return abs(x2-x1) == 1 and abs(y2-y1) == 1 \
            and p in visited and q in visited \
            and abs(visited[p] - visited[q]) == 1

    def _solve(self, graph, visited, node):
        if node in visited:
            return

        visited = visited.copy()
        visited[node] = len(visited)

        if node == self.end:
            if len(visited) == len(graph):
                yield visited
            return

        for n in graph[node]:
            if n not in visited and not self.are_crossing(n, node, visited):
                for soln in self._solve(graph, visited, n):
                    yield soln

parser.register_puzzle("twist", Twist)
parser.register_puzzle("twist-solution", TwistSolution)

def main():
    d = [
        "123",
        "321",
        "123",
    ]
    s = TwistSolver(d)
    for a in  s.solve():
        print(a)
        print()

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    main()