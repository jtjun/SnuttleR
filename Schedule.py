from Shuttle import Shuttle
import random
import copy


class Schedule:
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    def __init__(self, shuttles, serviced = []):
        self.shuttles = shuttles
        self.serviced = serviced
        pass

    def __str__(self):
        ret = ""
        for idx, shuttle in enumerate(self.shuttles):
            trip = shuttle.trip
            ret += "Shuttle {i}: {t}\n".format(i=idx, t=trip)
        return ret

    def __eq__(self, other):
        if len(self.trips) != len(other.trips):
            return False
        else:
            for i in range(len(self.trips)):
                if len(self.trips[i]) != len(other.trips[i]):
                    return False
                else:
                    for j in range(len(self.trips[i])):
                        if self.trips[i][j] != other.trips[i][j]: return False
            return True