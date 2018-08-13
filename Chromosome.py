import random
import copy

class Chromosome:
    # trip : an array of requests in order of visits (positive value: ride, negative value: drop off)
    # trips : [trip1, trip2, trip3, .. tripm]
    def __init__(self, trips):
        self.trips = trips
        self.trips.sort(key = lambda trip: len(trip))

    def __str__(self):
        ret = ""
        for idx, trip in enumerate(self.trips):
            ret += "Shuttle {i}: {t}\n".format(i = idx, t = trip)
        return ret

    def __eq__(self, other):
        if len(self.trips) != len(other.trips): return False
        else:
            for i in range(len(self.trips)):
                if len(self.trips[i]) != len(other.trips[i]): return False
                else:
                    for j in range(len(self.trips[i])):
                        if self.trips[i][j] != other.trips[i][j]: return False
            return True
        

    def mutation(self, x, y): # exchange the position of x and y
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
        pass

    def crossover(self, chromo): # remain half trips1, eleminate them from trips2 and merge two
        trips1 = copy.deepcopy(self.trips)
        trips2 = copy.deepcopy(chromo.trips)


        rettrips = copy.deepcopy(random.sample(trips1, (len(trips1)+1)//2))
        contained = set()
        
        for trip in rettrips:
            for r in trip:
                contained.add(r)

        for trip in trips2:
            tr = list(filter(lambda r: r not in contained, trip))
            if len(tr) > 0:
                rettrips.append(tr)
        
        return Chromosome(rettrips)

    def crossOver(self, chromo):
        trips = self.trips + chromo.trips
        ntrips = []
        rn = 0 # number of requests
        for trip in self.trips :
            rn += len(trip)//2
        markTable = []

        # search longest trip
        for i in range(rn) :
            i = i+1
            if i not in markTable : # not in ntrips
                idx = searchLongest(i, trips)
                trip = trips[idx][:]
                for t in trips[idx] :
                    if t in markTable :
                        trip.remove(t)

                ntrips.append(trip)
                markTable = markTable + trip

        return Chromosome(ntrips)

def searchLongest(a, lsts) :
    M = -1
    i = 0
    while i < len(lsts) :
        if a in lsts[i] :
            if M < 0 : M = i
            elif len(lsts[i]) > len(lsts[M]) : M = i
        i += 1
    return M