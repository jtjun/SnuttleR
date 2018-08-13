from Shuttle import Shuttle
import random
import copy

class DataGenerator:
    def __init__(self, MG, RG):
        self.dists = MG.dists
        self.depot = MG.depot
        self.distdepot = MG.distdepot
        self.requests = RG.requests
        self.m = len(self.dists) # number of stations
        self.n = len(self.requests) # number of requests
        self.T = RG.T

        self.L = self.makeL(self.requests) # time ordered trip containing all requests
        self.CT = self.conflictTable() # == C , index = Rn -1 (start with 0)
        self.S = self.makeSimilarRequest()
        pass

    def __str__(self):
        ret = ""
        return ret

    def makeL(self, requests):
        l = len(requests)
        L = list(range(1, l + 1)) + list(range(-l, 0))
        L.sort(key=lambda i: self.requests[abs(i) - 1][(abs(i) - i) // abs(i)])
        return L

    def subL(self, lst):
        trip = []
        for k in self.L:
            if abs(k) in lst: trip.append(k)
        return trip

    def conflictTable(self):
        l = len(self.requests)
        ct = [] # conflict table
        # -1 : conflict // 0 : i == j // 1 : available
        for i in range(l) :
            ct.append([])
            for j in range(l) :
                if i == j : ct[i].append(0)
                else :
                    trip = self.subL([i+1, j+1])
                    if self.available(trip) : ct[i].append(1)
                    else : ct[i].append(-1)
        return ct

    def chromoAble(self, chromo):
        trips = chromo.trips
        tripSet = []
        for trip in trips :
            if not self.available(trip) :
                # print("unavailable trip")
                return False
            tripSet += trip
        for i in range(len(self.requests)) :
            i = i+1
            if i not in tripSet :
                print("there are no %d in trips" %i)
                return False
            if -i not in tripSet :
                print("there are no %d in trips" % -i)
                return False
            if tripSet.count(i) != 1 :
                print("there are more %d s in trips" % i)
                return False
            if tripSet.count(-i) != 1 :
                print("there are more %d s in trips" % -i)
                return False
        return True

    def available(self, trip):
        ts = []
        stas = []
        l = 0
        for i in trip :
            ia = abs(i)
            ts.append(self.requests[ia-1][(ia-i)//ia])
            stas.append(self.requests[ia-1][((ia-i)//ia)+1])
            l += 1

        ats = [ts[0]]  # arrival times
        i = 0
        while i < l-1 :
            d = self.dists[stas[i]][stas[i+1]]
            at = ats[i]+d # arrival time

            if trip[i+1] < 0 : # drop off
                if ts[i+1] < at : return False # arrival late
                else : ats.append(at)

            if trip[i+1] > 0 : # pick up
                if ts[i+1] > at : ats.append(ts[i+1]) # arrival earlier
                # can calculate slack time at here
                else : ats.append(at)
            i += 1

        return True

    def getCost(self, chromo):
        COST_SHUTTLE = 1000
        cost = COST_SHUTTLE * len(chromo.trips)
        INF = 10000000
        if not self.chromoAble(chromo):
            return INF

        for trip in chromo.trips :
            l = len(trip)
            for i in range(l-1) :
                if trip[i]>0: staS = self.requests[trip[i]-1][1]
                else: staS = self.requests[-trip[i]-1][3]

                if trip[i+1]>0: staD = self.requests[trip[i+1]-1][1]
                else: staD = self.requests[-trip[i+1]-1][3]

                cost += self.dists[staS][staD]
            cost += self.distdepot[self.requests[trip[0]-1][1]] + self.distdepot[self.requests[-trip[-1]-1][3]]
        return cost

    def CFSSticingk(self, shuttle, t):
        reqs = filter(lambda r : r[4]<=t, self.requests[:])
        requests = list(enumerate(reqs))
        # considering requests which satisfy timeO <= t
        requests.sort(key=lambda request: request[1][2])
        trips = []

        routes = []
        # 

        # Cluster First
        L = self.makeL(reqs)

        for i in L :
            if i == L[0] :
                if len(trips) == 0 : routes.append([i])
            elif i > 0 :
                random.shuffle(routes)
                l = len(routes); j =0
                while j < l :
                    route = routes[j]
                    mutab =True # Mutually available
                    for r in route :
                        if self.CT[i-1][r-1] < 0 : mutab = False
                    if mutab :
                        route.append(i)
                        break
                    else : j+= 1
                if j == l : routes.append([i])

        # Sweep Second
        for route in routes :
            rtrips = self.splitRoute(route)
            trips += rtrips

        return Shuttle(trips)

    def splitRoute(self, route):
        tripr = self.subL(route)
        if len(route) <= 2 : return [tripr]
        elif self.available(tripr) : return [tripr]
        else :
            routeO = route[::2]
            routeE = route[1::2]
            return self.splitRoute(routeO) + self.splitRoute(routeE)