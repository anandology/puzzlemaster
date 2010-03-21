
def listget(list_, index, default=None):
    if index < len(list_):
        return list_[index]
    else:
        return default
        
def matrix2dict(m):
    """Convert a 2-D array to dictionary. The resultant dictionary can be indexed using (row, col).

        >>> d = matrix2dict([[1, 2], [3, 4], [5, 6]])
        >>> sorted(d.items())
        [((0, 0), 1), ((0, 1), 2), ((1, 0), 3), ((1, 1), 4), ((2, 0), 5), ((2, 1), 6)]
    """
    rows = len(m)
    cols = len(m[0])
    return dict(
        ((r, c), m[r][c])
        for r in range(rows) for c in range(cols))

def dict2matrix(d, default=" "):
    """Reverse of matrix2dict.

    >>> dict2matrix(matrix2dict([[1, 2], [3, 4], [5, 6]]))
    [[1, 2], [3, 4], [5, 6]]
    """
    rows = 1 + max(r for r, c in d)
    cols = 1 + max(c for r, c in d)    
    return [[d.get((r, c), default) for c in range(cols)] for r in range(rows)]
    
def matrix2str(m):
    r"""convert matrix to string.
    
        >>> matrix2str([[1, 2], [3, 4], [5, 6]])
        '12\n34\n56'
    """
    return "\n".join("".join(str(x) for x in row) for row in m)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()