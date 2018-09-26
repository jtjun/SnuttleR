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
        self.t = t

    def __str__(self):
        ret = ""
        ret += str(self.loc) + ' ' + str(self.getTrip())
        return ret

    def __eq__(self, other):
        tripi = self.getTrip()
        tripj = other.getTrip()
        if len(tripi) != len(tripj):
            return False
        else:
            for i in range(len(self.getTrip())):
                if tripi[i] != tripj[i]: return False
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

    def getTrip(self):
        return self.before + self.after