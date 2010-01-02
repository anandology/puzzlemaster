"""SVG rendering library.
"""
from __future__ import with_statement
from xml.etree import ElementTree
from StringIO import StringIO

class Node:
    """SVG Node"""
    def __init__(self, tag, **attrs):
        self.tag = tag
        self.attrs = dict((k.replace('_', '-'), unicode(v)) for k, v in attrs.items())
        self.children = []
        
    def node(self, tag, **attrs):
        n = Node(tag, **attrs)
        self.children.append(n)
        return n
        
    def __call__(self, *nodes):
        """Syntactic sugar for adding child nodes."""
        for n in nodes:
            self.add_node(n)

    def add_node(self, node):
        if not isinstance(node, Node):
            node = Text(node)
        self.children.append(node)

    def __getattr__(self, tag):
        return lambda **attrs: self.node(tag, **attrs)
        
    def translate(self, x, y):
        return self.g(transform="translate(%s, %s)" % (x, y))
        
    def scale(self, *args):
        return self.g(transform="scale(%s)" % ", ".join(str(a) for a in args))
        
    def __repr__(self):
        return "<%s .../>" % self.tag
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        pass
    
    def build_tree(self, builder):
        builder.start(self.tag, self.attrs)
        for node in self.children:
            node.build_tree(builder)
        return builder.end(self.tag)
        
    def _indent(self, elem, level=0):
        """Indent etree node for prettyprinting."""
        
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        
    def save(self, filename, encoding='utf-8'):
        f = open(filename, 'w')
        f.write(self.tostring())
        f.close()
        
    def tostring(self, encoding='utf-8'):
        builder = ElementTree.TreeBuilder()
        self.build_tree(builder)
        e = builder.close()
        self._indent(e)
        return ElementTree.tostring(e, encoding)
        
class Text(Node):
    """Text Node
        
        >>> p = Node("p")
        >>> p.add_text("hello, world!")
        >>> p.tostring()
        '<p>hello, world!</p>'
    """
    def __init__(self, text):
        Node.__init__(self, "__text__")
        self._text = text
    
    def build_tree(self, builder):
        builder.data(str(self._text))
        
class SVG(Node):
    """
        >>> svg = SVG(width=200, height=200)
        >>> svg.rect(x=0, y=0, width=200, height=200, fill="blue")
        <rect .../>
        >>> with svg.translate(-50, -50) as g:
        ...     g.rect(x=0, y=0, width=50, height=100, fill="red")
        ...     g.rect(x=50, y=0, width=50, height=100, fill="green")
        <rect .../>
        <rect .../>
        >>> print svg.tostring(),
        <svg height="200" width="200" xmlns="http://www.w3.org/2000/svg">
          <rect fill="blue" height="200" width="200" x="0" y="0" />
          <g transform="translate(-50, -50)">
            <rect fill="red" height="100" width="50" x="0" y="0" />
            <rect fill="green" height="100" width="50" x="50" y="0" />
          </g>
        </svg>
        
    """
    def __init__(self, **attrs):
        attrs['xmlns'] = "http://www.w3.org/2000/svg"
        Node.__init__(self, 'svg', **attrs)
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()