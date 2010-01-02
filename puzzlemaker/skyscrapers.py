"""Skyscrapers puzzle"""
from grid import Grid
import utils

__all__ = ["SkyScrappers"]

class SkyScrappers:
    def __init__(self, data):
        self.data = data
        self.size = len(data)-1
        
    @staticmethod
    def load(filename):
        data = [line.strip() for line in open(filename) if line.strip()]
        return SkyScrappers(data)
        
    def render(self):
        """Returns svg object."""
        grid = Grid(self.size, self.size)
        grid.draw_grid(stroke='black', stroke_width=2)
        
        for y, line in enumerate(self.data):
            for x, c in enumerate(line):
                if c not in " *":
                    attrs = {'font-weight': 'normal'}
                    
                    if y == self.size:
                        attrs['yoffset'] = 40
                        attrs['font-weight'] = 'bold'
                    if x == self.size:
                        attrs['xoffset'] = 20
                        attrs['font-weight'] = 'bold'
                    grid.text(x, y, c, **attrs)

        """
        def text(x, y, c, **kw):
            if c:
                grid.text(x, y, c, **kw)
        
        for i, c in enumerate(self.data[-1]):
            text(i, self.size, c, yoffset=40)
        
        for i, line in enumerate(self.data[:-1]):
            c = utils.listget(line, self.size)
            text(self.size, i, c, xoffset=20)
        """
        
        return grid.svg
                
def some(values):
    for v in values:
        if v:
            return v
    return False

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
    
class Solver:
    """Skyscraper solver inspired by Norvig's Sudoku solver.
    
    http://norvig.com/sudoku.html
    """
    def __init__(self, size, row_constraints, col_constraints):
        self.size = size
        self.row_constraints = row_constraints
        self.col_constraints = col_constraints
        
        rows = cols = range(size)
        squares = cross(rows, cols)
        digits = "".join(str(i) for i in range(1, size+1)) # assuming that the size will never be more than 9
        values = dict((s, digits) for s in squares)

        unitlists = [cross(rows, [c]) for c in cols] + [cross([r], cols) for r in rows]
        units = dict((s, [u for u in unitlists if s in u]) for s in squares)
        peers = dict((s, set(s2 for u in units[s] for s2 in u if s2 != s)) for s in squares)
        
        self.squares = squares
        self.digits = digits
        self.values = values
        self.units = units
        self.peers = peers
        
    def solve(self, findall=False):
        if findall:
            solutions = []
            def callback(s):
                solutions.append(s)
                return False
            self.search(self.values, callback)
            return solutions
        else:
            return self.search(self.values)

    def validate(self, values):
        for i, n in enumerate(self.row_constraints):
            if n in self.digits:
                heights = [values[i, j] for j in range(self.size)][::-1]
                if visible(heights) != int(n):
                    return False

        for j, n in enumerate(self.col_constraints):
            if n in self.digits:
                heights = [values[i, j] for i in range(self.size)][::-1]
                if visible(heights) != int(n):
                    return False

        return True

    def search(self, values, callback=None):
        if values is False:
            return False # Failed earlier

        if all(len(values[s]) == 1 for s in self.squares):
            if self.validate(values) is False:
                return False

            if callback:
                if callback(values) == False:
                    return False
                else:
                    return values
            else:
                return values # Solved!

        # Chose the unfilled square s with the fewest possibilities
        _, s = min((len(values[s]), s) for s in self.squares if len(values[s]) > 1)
        return some(self.search(self.assign(values.copy(), s, d), callback) 
                    for d in values[s])

    def assign(self, values, s, d):
        if all(self.eliminate(values, s, d2) for d2 in values[s] if d2 != d):
            return values
        else:
            return False
            
    def eliminate(self, values, s, d):
        #print 'eliminate', s, d, values[s]
        if d not in values[s]: # already eliminated
            return values
        values[s] = values[s].replace(d, '')

        if len(values[s]) == 0: #contradiction
            return False

        if len(values[s]) == 1:
            # only one value left in the square. remove it from all its peers
            d2 = values[s]
            #print 'peers', d2, peers[s]
            if not all(self.eliminate(values, s2, d2) for s2 in self.peers[s]):
                #print 'eliminate failed'
                return False

        ## Now check the places where d appears in the units of s
        for u in self.units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False
            elif len(dplaces) == 1:
                # d can only be in one place in unit; assign it there
                if not self.assign(values, dplaces[0], d):
                    return False
        return values

    def print_grid(self, values):
        if values is False:
            print values
            return
        width = 1 + max(len(v) for v in values.values())

        def hline():
            print '+' + "-" * width * self.size + '-+'

        print
        hline()
        for i in range(self.size):
            print "|" + "".join(values[i, j].center(width) for j in range(self.size)) + " | " + self.row_constraints[i]
        hline()
        print " " + "".join(str(c).center(width) for c in self.col_constraints)
        
def main(filename):
    puzzle = SkyScrappers.load(filename)
    size = puzzle.size
    data = puzzle.data
    solver = Solver(puzzle.size, [data[i][size] for i in range(size)], [data[size][i] for i in range(size)])
    
    solutions = solver.solve(findall=True)
    print "solutions:"
    for s in solutions:
        solver.print_grid(s)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
