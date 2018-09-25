import math


class Shuttle:
    # trip : an array of requests in order of visits
    # before : an array of requests already serviced
    # after : an array of requests which will be serviced
    # (positive value: ride, negative value: drop off)
    # trip[k] != 0, abs(trip[k]) > 0
    # loc : (x, y) tuple // location
    def __init__(self, loc, after, before=[], t=0):
        self.loc = loc
        self.after = after
        self.before = before
        self.trip = before + after
        self.t = t

    def __str__(self):
        ret = ""
        ret += str(self.loc) + ' ' + str(self.trip)
        return ret

    def __eq__(self, other):
        if len(self.trip) != len(other.trip):
            return False
        else:
            for i in range(len(self.trip)):
                if self.trip[i] != other.trip[i]: return False
            return True

    def moveTo(self, dest, t):
        self.t = t
        k = math.sqrt((self.loc[0] - dest[0]) ** 2 +\
                      (self.loc[1] - dest[1]) ** 2)
        if k <= 1.0:  # if distance < 1.0 waiting, elif distance == 1.0 apparently arrived
            self.loc = dest
        else:
            loc = (self.loc[0] + ((dest[0] - self.loc[0]) / k), \
                   self.loc[1] + ((dest[1] - self.loc[1]) / k))
            self.loc = loc

    def getCustomN(self):
        # reutrn current customers number
        custN = 0
        for r in self.before:
            if r > 0:
                custN += 1
            else:
                custN -= 1
        return custN