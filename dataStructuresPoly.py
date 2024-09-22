class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    # Comparison operators for sorting and equality checks
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
    
    def __repr__(self):
        return f"Segment(({self.p1.getX()}, {self.p1.getY()}) -> ({self.p2.getX()}, {self.p2.getY()}))"

class Polygon:
    def __init__(self, x, y):
        self.points = [Point(x, y)]  # Initialize with the first point
        self.segments = set()  # Set to store unique segments

    # Adds a new point and segment to the polygon, returns True if successful
    def addPoint(self, p):
        self.segments.add(Segment(self.points[-1].getX(), p.getX(), self.points[-1].getY(), p.getY()))
        self.points.append(p)
        return True
    
    # Ensures that the new segment doesn't cross any existing segments
    def notCrossingSegment(self, x, y):
        addingSeg = Segment(self.points[-1].getX(), x, self.points[-1].getY(), y)
        for segment in self.segments:
            if addingSeg.intersects(segment):
                return False
        return True
    
    # Closes the polygon by connecting the last point to the first
    def closePolygon(self):
        if len(self.points) > 2:
            self.segments.add(Segment(self.points[-1].getX(), self.points[0].getX(), self.points[-1].getY(), self.points[0].getY()))

    # Checks if the polygon is convex using cross product method
    def isConvex(self):
        if len(self.segments) < 4:
            return True  # A polygon with fewer than 4 segments is convex by definition
        
        sign = None
        n = len(self.points) - 2  # Iterate over triplets of points
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            p3 = self.points[i + 2]

            v1x = p2.getX() - p1.getX()
            v1y = p2.getY() - p1.getY()
            v2x = p3.getX() - p2.getX()
            v2y = p3.getY() - p2.getY()
             
            current_sign = v1x * v2y - v1y * v2x  # Cross product to check orientation
            if current_sign != 0:
                if sign is None:
                    sign = current_sign  # Set the initial sign
                elif sign * current_sign < 0:  # If orientation changes, it's concave
                    return False
                
        return True  # If all turns have the same orientation, it's convex
