"""Skyscrapers puzzle"""
import random

from .grid import Grid
from . import utils
from .parser import register_puzzle, parse_grid

__all__ = ["SkyScrappers"]

def xrepr(d):
    if isinstance(d, dict):
        size = 1 + max(x for x, y in d.keys())
        return " $ ".join(
            "|".join(d[row, col] for col in range(size))
            for row in range(size))
    else:
        return d

_tracelevel = 0
def trace(f):

    def g(self, *a, **kw):
        global _tracelevel
        print(" |  " * _tracelevel, '|--',  f.__name__, [xrepr(x) for x in a])
        _tracelevel += 1
        x = f(self, *a, **kw)
        _tracelevel -= 1
        return x
    return g

class SkyScrappersParser:
    def parse(self, lines):
        size = len(lines)-2
        grid = parse_grid(lines)

        constraints = {
            "top": {},
            "right": {},
            "bottom": {},
            "left": {},
        }
        for i in range(1, size+1):
            constraints['top'][i-1] = grid.pop((0, i), None)
            constraints['right'][i-1] = grid.pop((i, size+1), None)
            constraints['bottom'][i-1] = grid.pop((size+1, i), None)
            constraints['left'][i-1] = grid.pop((i, 0), None)

        grid = dict(((x-1, y-1), v) for (x, y), v in grid.items())

        """
        print size
        for key in constraints.keys():
            print key, repr("".join(constraints[key][i] or "-" for i in range(size)))

        for i in range(size):
            for j in range(size):
                print grid[i, j],
            print
        """
        return SkyScrappers(size, grid, constraints)

class SkyScrappers:
    def __init__(self, size, data, constraints):
        self.size = size
        self.data = data
        self.constraints = constraints

    @staticmethod
    def load(filename):
        data = [line.strip() for line in open(filename) if line.strip()]
        return SkyScrappers(data)

    @staticmethod
    def loads(text):
        data = [line.strip() for line in text.splitlines() if line.strip()]
        return SkyScrappers(data)

    def render(self):
        """Returns svg object."""
        grid = Grid(self.size, self.size)
        grid.draw_grid(stroke='black', stroke_width=2)

        def text(row, col, value, **attrs):
            if value is not None and value not in " *":
                grid.text(col, row, value, **attrs)

        # Draw all the values in the cells
        for (row, col), value in self.data.items():
            text(row, col, value, font_weight="normal")


        # Draw right constraints. Give 0.25 offset to draw numbers close to the border.
        for i, v in self.constraints['right'].items():
            text(i, self.size-0.25, v, font_weight='bold')

        for i, v in self.constraints['left'].items():
            text(i, -0.75, v, font_weight='bold')

        # Draw bottom constraints. Give 0.25 offset to draw numbers close to the border.
        for j, v in self.constraints['bottom'].items():
            text(self.size-0.25, j, v, font_weight='bold')

        for j, v in self.constraints['top'].items():
            text(-0.75, j, v, font_weight='bold')

        return grid.svg

    def solve(self):
        return Solver(self).solve()

    def solve_all(self):
        return Solver(self).solve_all()

    def __str__(self):
        d = self.data.copy()
        for i in range(self.size):
            d[i, self.size] = self.constraints['right'][i] or '*'
            d[self.size, i] = self.constraints['bottom'][i] or '*'
        d[self.size, self.size] = ""

        return "\n".join(
                    "".join(d[row, col] for col in range(self.size+1))
                    for row in range(self.size+1))

def some(values):
    for v in values:
        if v:
            return v
    return False

def iterjoin(iters):
    """Join the given list of iterators"""
    for it in iters:
        for x in it:
            yield x

def cross(A, B):
    return [(a, b) for a in A for b in B]

def visible(heights):
    tallest = 0
    n = 0
    for h in heights:
        h = int(h)
        if h > tallest:
            tallest = h
            n += 1
    return n

def rotate(seq):
    """Right rotate a sequence.
        >>> rotate([1, 2, 3])
        [2, 3, 1]
    """
    return seq[1:] + seq[:1]

class Generator:
    def __init__(self, size):
        self.size = size
        self.values = self.permute(self.initial_values(size), 10*size)

    def initial_values(self, size):
        values = []
        row = range(1, size+1)
        for i in range(size):
            values.append(row)
            row = rotate(row)
        return values

    def permute(self, values, n):
        def permute_rows(values):
            random.shuffle(values)
            return values

        def permute_cols(values):
            values = zip(*values)
            random.shuffle(values)
            return zip(*values)

        values = values[:]
        for i in range(n):
            values = permute_rows(values)
            values = permute_cols(values)
        return values

    def display(self, values=None):
        values = values or self.values
        for row in values:
            print(" ".join(str(d) for d in row))

class Solver:
    """Skyscraper solver inspired by Norvig's Sudoku solver.

    http://norvig.com/sudoku.html
    """
    def __init__(self, puzzle):
        self.size = puzzle.size
        self.constraints = puzzle.constraints

        size = self.size
        rows = cols = range(size)
        squares = cross(rows, cols)

        digits = "".join(str(i) for i in range(1, size+1)) # assuming that the size will never be more than 9

        values = puzzle.data.copy()
        for k in values:
            if values[k] == '*':
                values[k] = digits

        unitlists = [cross(rows, [c]) for c in cols] + [cross([r], cols) for r in rows]
        units = dict((s, [u for u in unitlists if s in u]) for s in squares)
        peers = dict((s, set(s2 for u in units[s] for s2 in u if s2 != s)) for s in squares)

        self.squares = squares
        self.digits = digits
        self.values = values
        self.units = units
        self.peers = peers

    def solve(self):
        it = self.solve_all()

        try:
            return it.next()
        except StopIteration:
            return None

    def solve_all(self):
        return (SkyScrappers(self.size, values, self.constraints) for values in self.search(self.values))

    def validate(self, values):
        """
            >>> puzzle = SkyScrappers(2, {(0, 0): 1, (0, 1): 2, (1, 0): 2, (1, 1): 1}, {"right": [1, '*'], "bottom": ["*", "*"]})
            >>> solver = Solver(puzzle)
            >>> solver.validate(puzzle.data)
            True
        """
        def validate_right(row):
            n = self.constraints['right'][row]
            # no constraint
            if str(n) not in self.digits:
                return True
            heights = [values[row, col] for col in range(self.size)][::-1]
            return visible(heights) == int(n)

        def validate_bottom(col):
            n = self.constraints['bottom'][col]
            # no constraint
            if str(n) not in self.digits:
                return True
            heights = [values[row, col] for row in range(self.size)][::-1]
            return visible(heights) == int(n)

        return all(validate_right(row) for row in range(self.size)) \
               and all(validate_bottom(col) for col in range(self.size))

    def debug(self, values, indent=""):
        sep = "\n" + indent
        print(indent + sep.join(
                    "|".join(values[row, col] for col in range(self.size))
                    for row in range(self.size)))

        def f(d):
            return "".join(str(d[i]) for i in range(len(d)))

        print(indent + "right", f(self.constraints['right']))
        print(indent + "bottom", f(self.constraints['bottom']))

    def search(self, values):
        if values is False or values == []:
            return [] # Failed earlier

        if all(len(values[s]) == 1 for s in self.squares):
            if self.validate(values) is False:
                return []
            else:
                return [values]

        # Choose the unfilled square s with the fewest possibilities
        _, s = min((len(values[s]), s) for s in self.squares if len(values[s]) > 1)

        return iterjoin(self.search(self.assign(values.copy(), s, d))
                    for d in values[s])

    def make_puzzle(self, values):
        return SkyScrappers(self.size, values, self.constraints)

    def assign(self, values, s, d, level=0):
        if values[s] == d:
            return values
        if all(self.eliminate(values, s, d2) for d2 in values[s] if d2 != d):
            return values
        else:
            return False

    def eliminate(self, values, s, d):
        if d not in values[s]: # already eliminated
            return values
        values[s] = values[s].replace(d, '')

        if len(values[s]) == 0: #contradiction
            return False

        if len(values[s]) == 1:
            # only one value left in the square. remove it from all its peers
            d2 = values[s]
            if not all(self.eliminate(values, s2, d2) for s2 in self.peers[s]):
                return False

        ## Now check the places where d appears in the units of s
        for u in self.units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False
            elif len(dplaces) == 1 and values[dplaces[0]] != d:
                # d can only be in one place in unit; assign it there if it is not already assigned
                if not self.assign(values, dplaces[0], d):
                    return False
        return values

    def print_grid(self, values):
        if values is False:
            print(values)
            return
        width = 1 + max(len(v) for v in values.values())

        def hline():
            print('+' + "-" * width * self.size + '-+')

        print()
        hline()
        for i in range(self.size):
            print("|" + "".join(values[i, j].center(width) for j in range(self.size)) + " | " + self.constraints['right'][i])
        hline()
        print(" " + "".join(str(c).center(width) for c in self.constraints['bottom']))


register_puzzle("skyscrapers", SkyScrappers)

def main(filename):
    puzzle = SkyScrappers.load(filename)
    size = puzzle.size
    data = puzzle.data
    solver = Solver(puzzle.size, [data[i][size] for i in range(size)], [data[size][i] for i in range(size)])

    solutions = solver.solve(findall=True)
    print("solutions:")
    for s in solutions:
        solver.print_grid(s)

def main(*a):
    g = Generator(6)
    g.display()

if __name__ == '__main__':
    import sys
    #main(sys.argv[1])
    text = open(sys.argv[1]).read().split('\n\n')[-1]
    puzzle = SkyScrappersParser().parse(text.splitlines())
    puzzle.render().save("1.svg")

    """
    i = 0
    for i, s in enumerate(puzzle.solve_all()):
        print s
        print
    print
    print 'found', i, 'solutions'
    """