def pointInsidePoly(point, poly, isConvex):
    x, y = point.getX(), point.getY()
    n = len(poly.points)
    
    if isConvex:
        for i in range(n):
            x1, y1 = poly.points[i].getX(), poly.points[i].getY()
            x2, y2 = poly.points[(i + 1) % n].getX(), poly.points[(i + 1) % n].getY()
            if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) < 0:
                return False
        return True
    else:
        inside = False
        p1x, p1y = poly.points[0].getX(), poly.points[0].getY()
        for i in range(n + 1):
            p2x, p2y = poly.points[i % n].getX(), poly.points[i % n].getY()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside