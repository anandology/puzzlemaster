"""Generic utility for drawing grids."""

from __future__ import with_statement

from svg import SVG

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        w = self.width*100 + 200
        h = self.height*100 + 200
        self.svg = SVG(width=w, height=h)
        self.canvas = self.svg.translate(100, 100)
        
    def hline(self, x, y, width, **attrs):
        self.line(x, y, x+width, y, **attrs)
        
    def vline(self, x, y, height, **attrs):
        self.line(x, y, x, y+height, **attrs)
        
    def line(self, x1, y1, x2, y2, **attrs):
        self.canvas.line(x1=x1*100, y1=y1*100, x2=x2*100, y2=y2*100, **attrs)
    
    def circle(self, cx, cy, r, **attrs):
        cx, cy = cx*100, cy*100
        self.canvas.circle(cx=cx, cy=cy, r=r, **attrs)
        
    def draw_grid(self, **attrs):
        # draw vertical lines
        for x in range(self.width+1):
            self.vline(x, 0, self.height, **attrs)

        # draw horizontal lines
        for y in range(self.height+1):
            self.hline(0, y, self.width, **attrs)
            
    def draw_corners(self, **attrs):
        attrs.setdefault("r", 3)
        
        for x in range(self.width+1):
            for y in range(self.height+1):
                self.circle(x, y, **attrs)
        
    def text(self, x, y, text, **attrs):
        defaults = dict(font_size=48, text_anchor="middle",  style="dominant-baseline: central;", font_family="Courier", font_weight="bold")
        attrs = dict(defaults, **attrs)
        
        xoffset = attrs.pop('xoffset', 50)
        yoffset = attrs.pop('yoffset', 65)
        
        x, y = x*100+xoffset, y*100+yoffset
        self.canvas.text(x=x, y=y, **attrs)(text)
        
    def draw_numbers(self, data, **attrs):
        """Draw numbers in each cell.
        """
        for (row, col), value in data.items():
            self.text(col, row, value, **attrs)
                
def main():
    g = Grid(4, 4)
    g.draw_grid(stroke="black", stroke_width=1, stroke_dasharray="2 2")
    g.draw_corners(stroke="black", r=5)
    g.text(0, 0, 123, font_size=48, text_anchor="middle",  style="dominant-baseline: central;", font_family="Courier", font_weight="bold")
    g.svg.save("a.svg")
    print 'saved to a.svg'      

if __name__ == '__main__':
    main()