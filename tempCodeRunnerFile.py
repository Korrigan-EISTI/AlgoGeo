def orientation(p, q, r):
    val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())
    if val == 0:
        return 0 
    elif val > 0:
        return 1 
    else:
        return 2 