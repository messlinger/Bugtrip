
def ir(x):  # for convenience: transform scalar or list to int
    try: return [int(round(i)) for i in x]  # try to iterate
    except: return int(round(x))


class Pos():
    def __init__(self, (x,y) ):
        self.x, self.y = x,y