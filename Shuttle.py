import random
import copy


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