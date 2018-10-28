from Shuttle import Shuttle
import random
import copy

class Schedule:
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    def __init__(self, shuttles, rejects = []):
        self.shuttles = shuttles
        accepts = []
        for shut in shuttles:
            accepts += (shut.before+shut.trip)
        self.rejects = list(filter(lambda r : r not in accepts, rejects))
        self.rejects.sort()
        self.shuttles.sort(key = lambda shut : len(shut.trip + shut.before))
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
                if len(self.shuttles[i].trip) != len(other.shuttles[i].trip):
                    return False
                else:
                    for j in range(len(self.shuttles[i].trip)):
                        if self.shuttles[i].trip[j] != other.shuttles[i].trip[j]: return False
            return True

    def getServiced(self, n):
        serviced = []
        allTrip = []
        for (i, shuttle) in enumerate(self.shuttles) :
            serviced += shuttle.before[:]
            trip = shuttle.before + shuttle.trip
            allTrip += trip

        noPos = []
        noNeg = []
        for i in range(1, n+1) :
            if i not in allTrip :
                noPos.append(i)
            if -i not in allTrip :
                noNeg.append(-i)

        print('{} {}'.format(noPos, len(noPos)))
        print('{} {}'.format(noNeg, len(noNeg)))
        print('')

        return serviced