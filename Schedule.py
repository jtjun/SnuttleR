from Shuttle import Shuttle
import random
import copy

class Schedule: # using as gene (chromosome)
    # shuttles : an array of shuttles [shuttle0, shuttle1, ...]
    # serviced : an array of requests which is serviced
    # rejects : an array of rejected requests
    # reqS : an array of requests which is considered

    def __init__(self, shuttles, reqS):
        self.shuttles = shuttles
        self.reqS = reqS
        self.reqN = len(reqS)
        accepts = []
        for shut in shuttles:
            accepts += (shut.before+shut.trip)
        self.rejects = list(filter(lambda r : r not in accepts, self.reqS))
        self.rejects.sort()
        self.shuttles.sort(key = lambda shut : len(shut.trip))
        pass

    def __str__(self):
        wholetrip = []
        for shuttle in self.shuttles:
            wholetrip += shuttle.trip

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
                if len(self.shuttles[i].trip) != len(other.shuttles[i].trip):
                    return False
                else:
                    for j in range(len(self.shuttles[i].trip)):
                        if self.shuttles[i].trip[j] != other.shuttles[i].trip[j]: return False
            return True

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
            trip = shut.trip
            for r in trip:
                contained.add(r)

        for shut in shuts2:
            tr = list(filter(lambda r: r not in contained, shut.trip))
            if len(tr) > 0:
                nshut = Shuttle(shut.loc, tr, [], shut.t)
                retshuts.append(nshut)

        if len(retshuts) > 10:
            retshuts.sort(key=lambda shut: -len(shut.trip))
            retshuts = retshuts[:10]

        return Schedule(retshuts, self.reqS)