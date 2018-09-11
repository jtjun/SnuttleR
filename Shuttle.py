import random
import copy
import math

class Shuttle:
    # trip : an array of requests in order of visits (positive value: ride, negative value: drop off)
    # trip[k] != 0, abs(trip[k]) > 0
    # location : (x, y) tuple
    def __init__(self, loc, trip, before, t = 0):
        self.loc = loc
        self.trip = trip
        # : trip[0] is always next destination
        # ie. every tick cut the trip by t
        self.before = before
        self.t = t

    def __str__(self):
        ret = ""
        ret += str(self.loc) +' '+ str(self.trip)
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
        k = math.sqrt((self.loc[0] - dest[0])**2 + (self.loc[1] - dest[1])**2)
        if  k <= 1.0: # if distance < 1.0 waiting, elif distance == 1.0 apparently arrived
            self.loc = dest
        else:
            loc = (self.loc[0] + ((dest[0] - self.loc[0])/k), \
                   self.loc[1] + ((dest[1] - self.loc[1])/k))
            self.loc = loc

    def getCustN(self):
        custN = 0
        for r in self.before :
            if r > 0 : custN += 1
            else : custN -= 1
        return custN