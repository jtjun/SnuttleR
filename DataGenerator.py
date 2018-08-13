from Chromosome import Chromosome
from Pool import Pool
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

        self.L = self.makeL() # time ordered trip containing all requests
        self.CT = self.conflictTable() # == C , index = Rn -1 (start with 0)
        self.S = self.makeSimilarRequest()
        pass

    def __str__(self):
        ret = ""
        return ret

    def makeL(self):
        l = len(self.requests)
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

    def makeSimilarRequest(self):
        ret = []
        for requestidx in range(self.n):
            rw = []
            request = self.requests[requestidx]
            su = 0.0
            for request2 in self.requests:
                dreq = (request2[0] - request[0])**2 + (request2[2] - request[2])**2 \
                       + (self.dists[request2[1]][request[1]])**2 + (self.dists[request2[3]][request[3]])**2
                if dreq>0: su += 1/dreq
            for request2 in self.requests:
                dreq = (request2[0] - request[0])**2 + (request2[2] - request[2])**2 \
                       + (self.dists[request2[1]][request[1]])**2 + (self.dists[request2[3]][request[3]])**2
                if dreq>0: rw.append(1/dreq/su)
                else: rw.append(0.0)
            ret.append(rw)
        return ret

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

    def generateRAND(self):
        m, n = self.m, self.n
        requests = list(range(1,n+1))
        random.shuffle(requests)
        divs = random.sample(range(1,n+1), m)
        divs.sort()

        trips = [requests[divs[-1]:]+requests[:divs[0]]]
        for i in range(1,m):
            trips.append(requests[divs[i-1]:divs[i]])
        # print(trips)

        for i in range(m):
            for j in range(len(trips[i]),0,-1):
                k = random.randrange(j,len(trips[i])+1)
                trips[i] = trips[i][:k] + [-trips[i][j-1]] + trips[i][k:]

        return Chromosome(trips)


    def generateOTOC(self):
        requests = list(enumerate(self.requests[:]))
        requests.sort(key = lambda request : request[1][2])
        # sort by timeD

        trips = []
        lasttime = []

        for reqn, request in requests:
            v = -1
            t = 0
            for i, time in enumerate(lasttime):
                dist = time[1][request[1]]
                if time[0] + dist < request[0]:
                    if t < time[0]:
                        v, t = i, time[0]
                
            if v==-1:
                trips.append([(reqn+1), -(reqn+1)])
                lasttime.append((request[2], self.dists[request[3]]))
            else:
                trips[v].extend([(reqn+1), -(reqn+1)])
                lasttime[v] = (request[2], self.dists[request[3]])

        return Chromosome(trips)

    def generateCFSS(self):
        requests = list(enumerate(self.requests[:]))
        requests.sort(key=lambda request: request[1][2])
        trips = []

        # Cluster First
        routes = []

        for i in self.L :
            if i == self.L[0] : routes.append([i])
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

        return Chromosome(trips)

    def splitRoute(self, route):
        tripr = self.subL(route)
        if len(route) <= 2 : return [tripr]
        elif self.available(tripr) : return [tripr]
        else :
            routeO = route[::2]
            routeE = route[1::2]
            return self.splitRoute(routeO) + self.splitRoute(routeE)

    def getSimilarRequest(self, requestidx):
        t = random.random()
        for i in range(self.n):
            if t < self.S[requestidx][i]:
                return i
            else:
                t -= self.S[requestidx][i]
        return self.n-1

    def mergeTrips(self, trip1, trip2):
        mint1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        mint2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]

        mint1[0][0] = 0
        mint2[0][0] = 0
        for i in range(len(trip1)+1):
            for j in range(len(trip2)+1):
                if i > 0:
                    if trip1[i-1] > 0: sta1 = self.requests[trip1[i-1]-1][1]
                    else: sta1 = self.requests[-trip1[i-1]-1][3]

                if j > 0:
                    if trip2[j-1] > 0: sta2 = self.requests[trip2[j-1]-1][1]
                    else: sta2 = self.requests[-trip2[j-1]-1][3]

                if i > 1:
                    if trip1[i-2] > 0: sta1p = self.requests[trip1[i-2]-1][1]
                    else: sta1p = self.requests[-trip1[i-2]-1][3]

                if j > 1:
                    if trip2[j-2] > 0: sta2p = self.requests[trip2[j-2]-1][1]
                    else: sta2p = self.requests[-trip2[j-2]-1][3]

                if i > 1:
                    if mint1[i-1][j] != -1 and (mint1[i][j] == -1 or mint1[i][j] > mint1[i-1][j] + self.dists[sta1p][sta1]):
                        mint1[i][j] = mint1[i-1][j] + self.dists[sta1p][sta1]
                        p1[i][j] = 1
                if i == 1:
                    if mint1[i-1][j] != -1 and (mint1[i][j] == -1 or mint1[i][j] > mint1[i-1][j] + self.distdepot[sta1]):
                        mint1[i][j] = mint1[i-1][j] + self.distdepot[sta1]
                        p1[i][j] = 1
                if i > 0 and j > 0:
                    if mint2[i-1][j] != -1 and (mint1[i][j] == -1 or mint1[i][j] > mint2[i-1][j] + self.dists[sta2][sta1]):
                        mint1[i][j] = mint2[i-1][j] + self.dists[sta2][sta1]
                        p1[i][j] = 2

                if i > 0:
                    if trip1[i-1] > 0:
                        if mint1[i][j] != -1 and mint1[i][j] < self.requests[trip1[i-1]-1][0]:
                            mint1[i][j] = self.requests[trip1[i-1]-1][0]
                    if trip1[i-1] < 0:
                        if mint1[i][j] != -1 and mint1[i][j] > self.requests[-trip1[i-1]-1][2]:
                            mint1[i][j] = -1
                
                if j > 0 and i > 0:
                    if mint1[i][j-1] != -1 and (mint2[i][j] == -1 or mint2[i][j] > mint1[i][j-1] + self.dists[sta1][sta2]):
                        mint2[i][j] = mint1[i][j-1] + self.dists[sta1][sta2]
                        p2[i][j] = 1
                if j > 1:
                    if mint2[i][j-1] != -1 and (mint2[i][j] == -1 or mint2[i][j] > mint2[i][j-1] + self.dists[sta2p][sta2]):
                        mint2[i][j] = mint2[i][j-1] + self.dists[sta2p][sta2]
                        p2[i][j] = 2
                if j == 1:
                    if mint2[i][j-1] != -1 and (mint2[i][j] == -1 or mint2[i][j] > mint2[i][j-1] + self.distdepot[sta2]):
                        mint2[i][j] = mint2[i][j-1] + self.distdepot[sta2]
                        p2[i][j] = 2

                if j > 0:
                    if trip2[j-1] > 0:
                        if mint2[i][j] != -1 and mint2[i][j] < self.requests[trip2[j-1]-1][0]:
                            mint2[i][j] = self.requests[trip2[j-1]-1][0]
                    if trip2[j-1] < 0:
                        if mint2[i][j] != -1 and mint2[i][j] > self.requests[-trip2[j-1]-1][2]:
                            mint2[i][j] = -1
        
        if mint1[-1][-1] == -1 and mint2[-1][-1] == -1:
            # print("Merge Trips Failed")
            return None
        else:
            ret = []
            p = 0
            i = len(trip1)
            j = len(trip2)
            if mint1[-1][-1] == -1: p = 2
            elif mint2[-1][-1] == -1: p = 1
            elif mint1[-1][-1] < mint2[-1][-1]: p = 1
            else: p = 2

            while i > 0 or j > 0:
                # print(p,i,j)
                if p == 1:
                    ret.append(trip1[i-1])
                    p = p1[i][j]
                    i -= 1
                else:
                    ret.append(trip2[j-1])
                    p = p2[i][j]
                    j -= 1
            ret.reverse()
            return ret
        
    def divideinto(self, tripsi):
        trips = copy.deepcopy(tripsi)
        i = 0
        l = len(trips)
        while i < l :
            ntrips = copy.deepcopy(self.tearApart(trips[i], trips))
            if len(ntrips) == len(trips) :
                i += 1
            else :
                trips = copy.deepcopy(ntrips)
                l = len(trips)
        return trips

    def tearApart(self, trip, trips):
        ntrips = copy.deepcopy(trips)
        ntrips.remove(trip)
        chec = []
        for x in trip :
            if x > 0 :
                for ntrip in ntrips :
                    tripi = ntrip[:] + [x, -x]
                    tripi.sort(key=lambda i: self.requests[abs(i) - 1][(abs(i) - i) // abs(i)])
                    if self.available(tripi) :
                        ntrips[ntrips.index(ntrip)] = copy.deepcopy(tripi)
                        chec = chec + [x, -x]
                        break
            if x not in chec : return trips

        for a in trip :
            if a not in chec : return trips
        return ntrips

    def tearApartt(self, trip, trips):
        ntrips = copy.deepcopy(trips)
        idx = trips.index(trip)

        chec = []
        for x in trip :
            if x > 0 :
                for i in range(idx+1, len(trips)) :
                    ntrip = ntrips[i]
                    tripi = ntrip[:] + [x, -x]
                    tripi.sort(key=lambda i: self.requests[abs(i) - 1][(abs(i) - i) // abs(i)])
                    if self.available(tripi) :
                        ntrips[ntrips.index(ntrip)] = copy.deepcopy(tripi)
                        chec = chec + [x, -x]
                        break

        if len(ntrips[idx]) == len(chec) : ntrips.remove(ntrips[idx])
        else :
            for a in chec:
                ntrips[idx].remove(a)
        return ntrips


    def r1i1(self, trips, n):
        if n >= self.n : return trips
        # it's fail to r1i1..

        l = len(trips) # select two trips randomly
        i1 = i2 = random.randrange(l)
        while i1 == i2 : i2 = random.randrange(l)
        trip1 = trips[i1]
        trip2 = trips[i2]

        drawi = trip2[:]
        random.shuffle(drawi)
        x = abs(drawi[0])
        # select one request from trip2 randomly

        tripi = trip1[:]
        tx = self.requests[x-1][0]
        tnx = self.requests[x-1][2]

        idx = 0 # insert 'x' to trip1
        while idx < len(tripi) :
            r = tripi[idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if t > tx :
                tripi = tripi[:idx] +[x]+ tripi[idx:]
                break
            idx += 1
        idx = 0 # insert '-x' to trip1
        while idx < len(tripi):
            r = tripi[idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if tnx > t :
                tripi = tripi[:idx] +[-x]+ tripi[idx:]
                break
            idx += 1
        # add selected request to trip1

        if self.available(tripi) :
            trips[i1] = tripi
            if len(trip2) == 2 :
                trips.remove(trip2)
            else :
                trip2.remove(x)
                trip2.remove(-x)
            return trips # if it's available : return result of r1i1
        else : # if it's not available : try agin
            return self.r1i1(trips, n+1)