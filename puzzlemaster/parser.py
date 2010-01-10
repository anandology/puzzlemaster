"""Puzzle parser

(part of puzzlemaster)
"""

import itertools

_puzzle_registry = {}

def register_puzzle(name, cls):
    _puzzle_registry[name] = cls
    
def split_kv(line):
    k, v = line.split(":", 1)
    return k.strip(), v.strip()

def parse(data):
    headers = []
    body = []
    
    lines = (line.strip() for line in data.splitlines())
    
    headers = dict(split_kv(line) for line in itertools.takewhile(lambda line: line, lines))
    body = "\n".join(lines)
    
    puzzle = headers['puzzle']
    return _puzzle_registry[puzzle].loads(body)
    
    
def parse_file(filename):
    return parse(open(filename).read())

