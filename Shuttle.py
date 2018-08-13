import random
import copy


class Shuttle:
    # trip : an array of requests in order of visits (positive value: ride, negative value: drop off)
    # trips : [trip1, trip2, trip3, .. tripm]
    # position : (x, y)
    def __init__(self, trips, depot):
        self.position = depot
        self.trips = trips
        self.trips.sort(key=lambda trip: len(trip))

    def __str__(self):
        ret = ""
        for idx, trip in enumerate(self.trips):
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
