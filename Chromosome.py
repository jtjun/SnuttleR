import random
import copy

class Chromosome:
    # trip : an array of requests in order of vists (positive value: ride, negative value: drop off)
    # trips : [trip1, trip2, ..., tripm]
    # rejects : an array of rejected requests
    # reqN : total number of requests
    
    def __init__(self, reqN, trips):
        self.reqN = reqN
        self.trips = copy.deepcopy(trips)
        self.trips.sort(key = lambda trip: len(trip))

        self.rejects = list(filter(lambda r: not any(r in trip for trip in self.trips), range(1, self.reqN+1)))

    def __str__(self):
        ret = "--------------------"
        ret += "Accepted: {a}, Rejected: {r}, Reject Ratio: {rr}\n".format(a = self.reqN - len(self.rejects), r = len(self.rejects), rr = len(self.rejects) / self.reqN)
        for idx, trip in enumerate(self.trips):
            ret += "Shuttle {i}: {t}\n".format(i = idx, t = trip)
        ret += "Rejected: {r}\n".format(r = self.rejects)
        return ret

    def mutation(self, x, y): # change position of request x and request y
        for trip in self.trips:
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
        retreqN = max([self.reqN, other.reqN])
        trips1 = copy.deepcopy(self.trips)
        trips2 = copy.deepcopy(other.trips)

        rettrips = copy.deepcopy(random.sample(trips1, (len(trips1)+1)//2))
        contained = set()

        for trip in rettrips:
            for r in trip:
                contained.add(r)

        for trip in trips2:
            tr = list(filter(lambda r: r not in contained, trip))
            if len(tr) > 0:
                rettrips.append(tr)

        if len(rettrips) > 10:
            rettrips.sort(key = lambda trip: -len(trip))
            rettrips = rettrips[:10]
        
        return Chromosome(retreqN, rettrips)