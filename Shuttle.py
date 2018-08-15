import random
import copy
import math

class Shuttle:
    # trip : an array of requests in order of visits (positive value: ride, negative value: drop off)
    # location : (x, y) tuple
    def __init__(self, loc, trip, t):
        self.loc = loc
        self.trip = trip
        self.serviced = []
        self.t  = t

    def __str__(self):
        ret = ""
        ret += self.loc +' '+ self.trip
        return ret

    def __eq__(self, other):
        if len(self.trip) != len(other.trip):
            return False
        else:
            for i in range(len(self.trip)):
                if self.trip[i] != other.trip[i]: return False
            return True
    
    def moveTo(self, dest):
        k = math.sqrt((self.loc[0] - dest[0])**2 + (self.loc[1] - dest[1])**2)
        if  k <= 1.0:
            self.loc = dest
        else:
            self.loc[0] += (dest[0] - self.loc[0]) / k
            self.loc[1] += (dest[1] - self.loc[1]) / k