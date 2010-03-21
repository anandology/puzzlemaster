"""Command Line Interface to puzzlemaster"""
import sys
import os.path

import parser
import skyscrapers
import loop
import twist

def main():
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = dict(render=render, help=help, solve=solve)
    if cmd in commands:
        commands[cmd](*args)
    else:
        print "unknown command", cmd
    
def render(*puzzle_files):
    for puzzle_file in puzzle_files:
        svg = parser.parse_file(puzzle_file).render().tostring()
        filename = os.path.splitext(puzzle_file)[0] + '.svg'
        f = open(filename, 'w')
        f.write(svg)
        f.close()
        print 'generated', filename
        
def solve(puzzle_file):
    puzzle = parser.parse_file(puzzle_file)
    
    solutions = list(puzzle.solve())
    
    count = 0
    for s in solutions:
        count += 1
        print s
        print
    
    print "%d solutions found" % count

    """
    filename = os.path.splitext(puzzle_file)[0] + '-s.svg'
    f = open(filename, 'w')
    f.write(solutions[0].render().tostring())
    f.close()
    print 'generated', filename
    """
    
if __name__ == "__main__":
    main()
