from Shuttle import Shuttle
import random
import copy

class Schedule: # using as chromosome
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    # rejects : an array of rejected requests
    # reqS : all considered requests

    def __init__(self, shuttles, reqS):
        self.shuttles = shuttles
        self.reqS = reqS
        accepts = []
        for shut in shuttles:
            accepts += (shut.before+shut.trip)
        self.rejects = list(filter(lambda r : r not in accepts, self.reqS))
        self.rejects.sort()
        self.shuttles.sort(key = lambda shut : len(shut.trip + shut.before))
        pass

    def __str__(self):
        wholetrip = []
        for shuttle in self.shuttles:
            trip = shuttle.trip
            wholetrip += trip

        ret = "--------------------"
        ret += "{w} Considered: {a}, Rejected: {r}, Reject Ratio: {rr}\n" \
            .format(w=self.reqN, a=len(wholetrip) // 2, r=len(self.rejects), rr=len(self.rejects) / self.reqN)
        for idx, shuttle in enumerate(self.shuttles):
            ret += "Shuttle {i}: {b}|{a}\n".format(i=idx, b=shuttle.before, a=shuttle.after)
        ret += "Rejected: {r}".format(r=self.rejects)
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
            trip = shuttle.trip
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
            after = shuttle.after
            for i in range(len(after)):
                if after[i] == x:
                    after[i] = y
                elif after[i] == -x:
                    after[i] = -y
                elif after[i] == y:
                    after[i] = x
                elif after[i] == -y:
                    after[i] = -x

        for i in range(len(self.rejects)):
            if self.rejects[i] == x:
                self.rejects[i] = y
            elif self.rejects[i] == y:
                self.rejects[i] = x

    def crossover(self, other):
        # only when t = 0
        shuts1 = copy.deepcopy(self.shuttles)
        shuts2 = copy.deepcopy(other.shuttles)

        retshuts = copy.deepcopy(random.sample(shuts1, (len(shuts1) + 1) // 2))
        contained = set()

        for shuttle in retshuts:
            after = shuttle.after
            for r in after:
                contained.add(r)

        for shuttle in shuts2:
            after = shuttle.after
            aftr = list(filter(lambda r: r not in contained, after))
            if len(aftr) > 0:
                nshut = Shuttle(shuttle.loc, aftr, shuttle.before, shuttle.t)
                retshuts.append(nshut)

        if len(retshuts) > 10:
            retshuts.sort(key=lambda shut: -len(shut.after))
            retshuts = retshuts[:10]

        return Schedule(retshuts, self.reqS)