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

    def mutation(self, x, y): # change position of request x and request y
        # only when t = 0 : there are no servicing process
        # shut.loc = depot | shut.before = [] | *rejects is not empty*
        for shut in self.shuttles:
            trip = shut.trip
            for i in range(len(trip)):
                if trip[i] == x:
                    trip[i] = y
                elif trip[i] == -x:
                    trip[i] = -y
                elif trip[i] == y:
                    trip[i] = x
                elif trip[i] == -y:
                    trip[i] = -x

        for i in range(len(self.rejects)):
            if self.rejects[i] == x:
                self.rejects[i] = y
            elif self.rejects[i] == y:
                self.rejects[i] = x

    def crossover(self, other):
        # only when t = 0 : there are no servicing process
        # shut.loc = depot | shut.before = [] | *rejects is not empty*
        reqs = self.rejects[:] # whole reqs which in schedule
        for shut in self.shuttles:
            reqs += (shut.before+shut.trip)

        shuts1 = copy.deepcopy(self.shuttles)
        shuts2 = copy.deepcopy(other.shuttles)

        retshuts = copy.deepcopy(random.sample(shuts1, (len(shuts1) + 1) // 2))
        contained = []

        for shut in retshuts:
            contained += (shut.before + shut.trip)

        for shut in shuts2:
            ntrip = list(filter(lambda r : r not in contained, shut.trip))
            if len(ntrip) > 0:
                nshut = Shuttle(shut.loc, ntrip, [], 0)
                retshuts.append(nshut)

        if len(retshuts) > 10:
            retshuts.sort(key=lambda shut: -len(shut.trip))
            retshuts = retshuts[:10]

        accepts = []
        for shut in retshuts:
            accepts += shut.trip
        rejects = []
        for r in reqs :
            if r not in accepts: rejects.append(r)

        return Schedule(retshuts, rejects)