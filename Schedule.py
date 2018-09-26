from Shuttle import Shuttle
import random
import copy

class Schedule: # using as gene (chromosome)
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    # rejects : an array of rejected requests
    # reqS : an array of requests which is considered
    # reqN: number of considered requests

    def __init__(self, shuttles, reqS=[]):
        self.shuttles = shuttles
        self.reqS = reqS
        self.reqN = len(reqS)
        accepts = []
        for shut in shuttles:
            accepts += shut.getTrip()
        self.rejects = list(filter(lambda r : r not in accepts, self.reqS))
        self.rejects.sort()
        self.shuttles.sort(key = lambda shut : len(shut.getTrip()))
        pass

    def __str__(self):
        wholetrip = []
        for shuttle in self.shuttles:
            wholetrip += shuttle.getTrip()

        ret = "--------------------"
        ret += "{w} Accepted: {a}, Rejected: {r}, Reject Ratio: {rr}\n" \
            .format(w=self.reqN, a=len(wholetrip) // 2, r=len(self.rejects), rr=len(self.rejects)/self.reqN)

        for idx, shuttle in enumerate(self.shuttles):
            after = shuttle.after
            before = shuttle.before
            ret += "Shuttle {i}: {b} {t}\n".format(i=idx, b = before, t=after)

        return ret

    def __eq__(self, other):
        if len(self.shuttles) != len(other.shuttles):
            return False
        else:
            for i in range(len(self.shuttles)):
                if self.shuttles[i] != other.shuttles[i]:
                    return False
            return True

    def getServiced(self, n):
        serviced = []
        allTrip = []
        for (i, shuttle) in enumerate(self.shuttles) :
            serviced += shuttle.before[:]
            trip = shuttle.getTrip()
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

    def mutation(self, x, y):
        # change position of request x and request y
        # only when t = 0
        for shuttle in self.shuttles:
            trip = shuttle.after
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
        shuts1 = copy.deepcopy(self.shuttles)
        shuts2 = copy.deepcopy(other.shuttles)

        retshuts = copy.deepcopy(random.sample(shuts1, (len(shuts1) + 1) // 2))
        contained = set()

        for shut in retshuts:
            trip = shut.getTrip()
            for r in trip:
                contained.add(r)

        for shut in shuts2:
            trip = shut.getTrip()
            tr = list(filter(lambda r: r not in contained, trip))
            if len(tr) > 0:
                nshut = Shuttle(shut.loc, tr, [], shut.t)
                retshuts.append(nshut)

        if len(retshuts) > 10:
            retshuts.sort(key=lambda shut: -len(shut.getTrip()))
            retshuts = retshuts[:10]

        return Schedule(retshuts, self.reqS)