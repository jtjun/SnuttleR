from Shuttle import Shuttle
import random
import copy


class Schedule:
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    def __init__(self, shuttles, rejects = []):
        self.shuttles = shuttles
        self.serviced = []
        self.rejects = rejects
        self.rejects.sort()
        pass

    def __str__(self):
        ret = ""
        for idx, shuttle in enumerate(self.shuttles):
            trip = shuttle.trip
            before = shuttle.before
            ret += "Shuttle {i}: {b} {t}\n".format(i=idx, b = before, t=trip)
        return ret

    def __eq__(self, other):
        if len(self.shuttles) != len(other.shuttles):
            return False
        else:
            for i in range(len(self.shuttles)):
                if len(self.shuttles[i]) != len(other.shuttles[i]):
                    return False
                else:
                    for j in range(len(self.shuttles[i])):
                        if self.shuttles[i][j] != other.shuttles[i][j]: return False
            return True

    def getServiced(self):
        serviced = []
        allTrip = []
        for (i, shuttle) in enumerate(self.shuttles) :
            serviced += shuttle.before[:]
            trip = shuttle.before + shuttle.trip
            allTrip += trip

        noPos = []
        noNeg = []
        for i in range(1, 71) :
            if i not in allTrip :
                noPos.append(i)
            if -i not in allTrip :
                noNeg.append(-i)

        print('{} {}'.format(noPos, len(noPos)))
        print('{} {}'.format(noNeg, len(noNeg)))
        print('')

        self.serviced = serviced
        return serviced
