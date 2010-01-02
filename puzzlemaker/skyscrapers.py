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
        

class Solver:
    def __init__(self, rows, cols):
        self.size = len(rows)
        self.rows = rows
        self.cols = cols
        
        self.cells = 1
        
def some(values):
    for v in values:
        if v:
            return v
    return False

def cross(A, B):
    return [(a, b) for a in A for b in B]

def solve(size, row_constraints, col_constraints, findall=False):
    """Skyscraper solver inspired by Norvig's Sudoku solver.
    
    http://norvig.com/sudoku.html
    """
    rows = cols = range(size)
    squares = cross(rows, cols)
    digits = "".join(str(i) for i in range(1, size+1)) # assuming that the size will never be more than 9
    values = dict((s, digits) for s in squares)
    
    unitlists = [cross(rows, [c]) for c in cols] + [cross([r], cols) for r in rows]
    units = dict((s, [u for u in unitlists if s in u]) for s in squares)
    peers = dict((s, set(s2 for u in units[s] for s2 in u if s2 != s)) for s in squares)
    
    def visible(heights):
        tallest = 0
        n = 0
        for h in heights:
            h = int(h)
            if h > tallest:
                tallest = h
                n += 1
        return n
    
    def validate(values):
        for i, n in enumerate(row_constraints):
            if n in digits:
                heights = [values[i, j] for j in range(size)][::-1]
                if visible(heights) != int(n):
                    return False
                    
        for j, n in enumerate(col_constraints):
            if n in digits:
                if visible(values[i, j] for i in range(size)) != int(n):
                    return False
                
        return True
        
    result = []
    
    def search(values):
        if values is False:
            return False # Failed earlier
            
        if all(len(values[s]) == 1 for s in squares):
            if validate(values) is False:
                return False

            if findall:
                result.append(values.copy())
                return False
            else:
                return values # Solved!
        
        # Chose the unfilled square s with the fewest possibilities
        _, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
        return some(search(assign(values.copy(), s, d)) 
                    for d in values[s])
                    
    def assign(values, s, d):
        #print 'assign', s, d
        #print_grid(values)
        if all(eliminate(values, s, d2) for d2 in values[s] if d2 != d):
            return values
        else:
            return False
            
    def eliminate(values, s, d):
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
            if not all(eliminate(values, s2, d2) for s2 in peers[s]):
                #print 'eliminate failed'
                return False
                
        ## Now check the places where d appears in the units of s
        for u in units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False
            elif len(dplaces) == 1:
                # d can only be in one place in unit; assign it there
                if not assign(values, dplaces[0], d):
                    return False
        return values

    def print_grid(values):
        if values is False:
            print values
            return
        width = 1 + max(len(v) for v in values.values())
        
        def hline():
            print '+' + "-" * width * size + '-+'
        
        print
        hline()
        for i in range(size):
            print "|" + "".join(values[i, j].center(width) for j in range(size)) + " | " + row_constraints[i]
        hline()
        print " " + "".join(str(c).center(width) for c in col_constraints)
    
    values = search(values)
    if findall:
        return result
    else:
        return values

def main2(filenames):
    import os
    
    for f in filenames:
        puzzle = SkyScrappers.load(f)
        svg = puzzle.render()
        
        f_svg = f.replace('.txt', '.svg')
        
        svg.save(f_svg)
        os.system('svg2png %s' % f_svg)
        print 'rendering', f
        
def main(filename):
    puzzle = SkyScrappers.load(filename)
    size = puzzle.size
    data = puzzle.data
    solutions = solve(puzzle.size, [data[i][size] for i in range(size)], [data[size][i] for i in range(size)], findall=True)
    for s in solutions:
        print_grid(s)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
