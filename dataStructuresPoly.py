
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
    
    def __hash__(self):
        return hash((self.x, self.y))

class Segment:
    def __init__(self, xA, xB, yA, yB):
        self.p1 = Point(xA, yA)
        self.p2 = Point(xB, yB)
         
    def intersects(self, other):
        A1, A2 = self.p1, self.p2
        B1, B2 = other.p1, other.p2
        
        v1 = (A2.x - A1.x, A2.y - A1.y)
        v2 = (B2.x - B1.x, B2.y - B1.y)

        r = (B1.x - A1.x, B1.y - A1.y)

        det = v1[0] * v2[1] - v1[1] * v2[0]
        if det == 0:
            return False 
        
        t = (r[0] * v2[1] - r[1] * v2[0]) / det
        u = (r[0] * v1[1] - r[1] * v1[0]) / det

        return (0 <= t <= 1) and (0 <= u <= 1)
    
    def __repr__(self):
        return f"Segment(({self.p1.getX()}, {self.p1.getY()}) -> ({self.p2.getX()}, {self.p2.getY()})"

class Polygon:
    def __init__(self, x, y):
        self.points = [Point(x, y)]
        self.segments = set()

    def addPoint(self, p):
        #if self.notCrossingSegment(p.getX(), p.getY()):
            self.segments.add(Segment(self.points[-1].getX(), p.getX(), self.points[-1].getY(), p.getY()))
            self.points.append(p)
            return True
        #return False
    
    def notCrossingSegment(self, x, y):
        addingSeg = Segment(self.points[-1].getX(), x, self.points[-1].getY(), y)
        for segment in self.segments:
            if addingSeg.intersects(segment):
                return False
        return True
    
    def closePolygon(self):
        if len(self.points) > 2:
            self.segments.add(Segment(self.points[-1].getX(), self.points[0].getX(), self.points[-1].getY(), self.points[0].getY()))

    def isConvex(self):
        if len(self.segments) < 4 : 
            return True
        
        sign = None
        n = len(self.points) - 2
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            p3 = self.points[i + 2]

            v1x = p2.getX() - p1.getX()
            v1y = p2.getY() - p1.getY()
            v2x = p3.getX() - p2.getX()
            v2y = p3.getY() - p2.getY()
             
            current_sign =  v1x * v2y - v1y * v2x
            if current_sign != 0:
                if sign is None:
                    sign = current_sign
                elif sign * current_sign < 0:
                    return False
                
        return True
    
    