from Chromosome import Chromosome
from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
import random
import copy

class DataGeneratorGA:
    def __init__(self, Map, Reqs, shutN):
        self.Map = Map
        self.Reqs = Reqs

        self.L = self.makeL()
        self.CT = self.conflictTable()
        self.S = self.makeSimilarRequest()
        self.depot = Map.depot
        self.shutN = shutN
        self.requests = Reqs.requests
        self.MG = Map
        self.dists = self.MG.dists
        
    
    def __str__(self):
        ret = "---------Map--------\n"
        ret += str(self.Map)
        ret += "--------Reqs--------\n"
        ret += str(self.Reqs)
        ret += "--------------------\n"
        return ret

    def makeL(self):
        l = self.Reqs.reqN
        L = list(range(1, l+1)) + list(range(-l, 0))
        L.sort(key = lambda i: self.Reqs.requests[abs(i) - 1][(abs(i) - i) // abs(i)])
        return L

    def subL(self, lst):
        return list(filter(lambda k: abs(k) in lst, self.L))

    def conflictTable(self):
        l = self.Reqs.reqN
        ct = [] # conflict table
        # -1: conflict
        # 0 : identical
        # 1 : available
        for i in range(l):
            ct.append([])
            for j in range(l):
                if i == j: ct[i].append(0)
                else:
                    trip = self.subL([i+1, j+1])
                    if self.available(trip): ct[i].append(1)
                    else: ct[i].append(-1)
        return ct

    def makeSimilarRequest(self):
        ret = []
        for requestidx in range(self.Reqs.reqN):
            rw = []
            request = self.Reqs.requests[requestidx]
            su = 0.0
            for request2 in self.Reqs.requests:
                dreq = (request2[0] - request[0])**2 + (request2[2] - request[2])**2 \
                       + (self.Map.dists[request2[1]][request[1]])**2 + (self.Map.dists[request2[3]][request[3]])**2
                if dreq > 0: su += 1/dreq
            
            for request2 in self.Reqs.requests:
                dreq = (request2[0] - request[0])**2 + (request2[2] - request[2])**2 \
                       + (self.Map.dists[request2[1]][request[1]])**2 + (self.Map.dists[request2[3]][request[3]])**2
                if dreq > 0: rw.append((1 / dreq) / su)
                else: rw.append(0.0)
            ret.append(rw)
        return ret
    
    def chromoAble(self, chromo):
        trips = chromo.trips
        tripSet = []

        for trip in trips:
            if not self.available(trip):
                return False
            tripSet += trip
        
        for i in range(self.Reqs.reqN):
            i += 1
            if tripSet.count(i) > 1 :
                print("there are more %d s in trips" % i)
                return False
            if tripSet.count(-i) > 1 :
                print("there are more %d s in trips" % -i)
                return False
        return True

    def available(self, trip):
        ts = []
        stas = []
        l = 0
        for i in trip:
            ia = abs(i)
            ts.append(self.Reqs.requests[ia - 1][(ia - i) // ia])
            stas.append(self.Reqs.requests[ia - 1][((ia - i) // ia) + 1])
            l += 1
        
        ats = [ts[0]]
        
        for i in range(l - 1):
            d = self.Map.dists[stas[i]][stas[i+1]]
            at = ats[i] + d

            if trip[i+1] < 0:
                if ts[i+1] < at: return False
                else: ats.append(at)
            
            if trip[i+1] > 0:
                if ts[i+1] > at: ats.append(ts[i+1])
                else: ats.append(at)

        return True

    def getCost(self, chromo):
        if not self.chromoAble(chromo):
            return 2.0*chromo.reqN

        sk = chromo.reqN
        for trip in chromo.trips:
            ts = []
            stas = []
            l = 0
            for i in trip:
                ia = abs(i)
                ts.append(self.Reqs.requests[ia - 1][(ia - i) // ia])
                stas.append(self.Reqs.requests[ia - 1][((ia - i) // ia) + 1])
                l += 1
            
            ats = [ts[0]]
            
            for i in range(l - 1):
                d = self.Map.dists[stas[i]][stas[i+1]]
                at = ats[i] + d

                if trip[i+1] < 0:
                    if ts[i+1] < at: return False
                    else: ats.append(at)
                
                if trip[i+1] > 0:
                    if ts[i+1] > at:
                        sk += (ts[i+1] - at) / self.Reqs.T
                        ats.append(ts[i+1])
                    else: ats.append(at)

        return len(chromo.rejects) + chromo.reqN/sk

    def generateCFSS(self):
        requests = list(enumerate(self.Reqs.requests[:]))
        requests.sort(key = lambda request: request[1][2]) # sort by deadline

        trips = []

        # Cluster
        routes = []
        for i in self.L:
            if i == self.L[0]: routes.append([i])
            elif i > 0:
                random.shuffle(routes)
                l = len(routes)

                p = True
                
                for j in range(l):
                    route = routes[j]
                    mutab = True
                    for r in route:
                        if self.CT[i-1][r-1] < 0: mutab = False
                    if mutab:
                        route.append(i)
                        p = False
                        break
                
                if p: routes.append([i])
        

        # Sweep
        for route in routes:
            rtrips = self.splitRoute(route)
            trips += rtrips

        trips.sort(key = lambda trip: -len(trip))
        trips = trips[:10]
        
        return Chromosome(self.Reqs.reqN, trips)

    def splitRoute(self, route):
        tripr = self.subL(route)
        if len(route) <= 2: return [tripr]
        elif self.available(tripr): return [tripr]
        else:
            routeO = route[::2]
            routeE = route[1::2]
            return self.splitRoute(routeO) + self.splitRoute(routeE)

    def getSimilarRequest(self, requestidx):
        t = random.random()
        for i in range(self.Reqs.reqN):
            if t < self.S[requestidx][i]:
                return i
            else:
                t -= self.S[requestidx][i]
        return self.Reqs.reqN - 1

    def mergeTrips(self, trip1, trip2):
        mint1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        mint2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]

        mint1[0][0] = 0
        mint2[0][0] = 0
        trip1 = [0] + trip1
        trip2 = [0] + trip2
        for i in range(len(trip1)): # the number of requests done in trip1
            for j in range(len(trip2)): # the number of requests done in trip2
                if i == 0: sta1 = 0
                else:
                    if trip1[i] > 0: sta1 = self.Reqs.requests[trip1[i]-1][1]
                    else: sta1 = self.Reqs.requests[-trip1[i]-1][3]

                    if i == 1: sta1p = 0
                    else:
                        if trip1[i-1] > 0: sta1p = self.Reqs.requests[trip1[i-1]-1][1]
                        else: sta1p = self.Reqs.requests[-trip1[i-1]-1][3]
                
                if j == 0: sta2 = 0
                else:
                    if trip2[j] > 0: sta2 = self.Reqs.requests[trip2[j]-1][1]
                    else: sta2 = self.Reqs.requests[-trip2[j]-1][3]
                    
                    if j == 1: sta2p = 0
                    else:
                        if trip2[j-1] > 0: sta2p = self.Reqs.requests[trip2[j-1]-1][1]
                        else: sta2p = self.Reqs.requests[-trip2[j-1]-1][3]

                if i > 0:
                    if mint1[i-1][j] != -1 and (mint1[i][j] == -1 or mint1[i][j] > mint1[i-1][j] + self.Map.dists[sta1p][sta1]):
                        mint1[i][j] = mint1[i-1][j] + self.Map.dists[sta1p][sta1]
                        p1[i][j] = 1
                    if mint2[i-1][j] != -1 and (mint1[i][j] == -1 or mint1[i][j] > mint2[i-1][j] + self.Map.dists[sta2][sta1]):
                        mint1[i][j] = mint2[i-1][j] + self.Map.dists[sta2][sta1]
                        p1[i][j] = 2

                    if trip1[i] > 0:
                        if mint1[i][j] != -1 and mint1[i][j] < self.Reqs.requests[trip1[i]-1][0]:
                            mint1[i][j] = self.Reqs.requests[trip1[i]-1][0]
                    if trip1[i] < 0:
                        if mint1[i][j] != -1 and mint1[i][j] > self.Reqs.requests[-trip1[i]-1][2]:
                            mint1[i][j] = -1
                
                if j > 0:
                    if mint1[i][j-1] != -1 and (mint2[i][j] == -1 or mint2[i][j] > mint1[i][j-1] + self.Map.dists[sta1][sta2]):
                        mint2[i][j] = mint1[i][j-1] + self.Map.dists[sta1][sta2]
                        p2[i][j] = 1
                    if mint2[i][j-1] != -1 and (mint2[i][j] == -1 or mint2[i][j] > mint2[i][j-1] + self.Map.dists[sta2p][sta2]):
                        mint2[i][j] = mint2[i][j-1] + self.Map.dists[sta2p][sta2]
                        p2[i][j] = 2

                    if trip2[j] > 0:
                        if mint2[i][j] != -1 and mint2[i][j] < self.Reqs.requests[trip2[j]-1][0]:
                            mint2[i][j] = self.Reqs.requests[trip2[j]-1][0]
                    if trip2[j] < 0:
                        if mint2[i][j] != -1 and mint2[i][j] > self.Reqs.requests[-trip2[j]-1][2]:
                            mint2[i][j] = -1
        
        if mint1[-1][-1] == -1 and mint2[-1][-1] == -1:
            # print("Merge Trips Failed")
            return None
        else:
            ret = []
            p = 0
            i = len(trip1) - 1
            j = len(trip2) - 1
            if mint1[-1][-1] == -1: p = 2
            elif mint2[-1][-1] == -1: p = 1
            elif mint1[-1][-1] < mint2[-1][-1]: p = 1
            else: p = 2

            while i > 0 or j > 0:
                # print(p,i,j)
                if p == 1:
                    ret.append(trip1[i])
                    p = p1[i][j]
                    i -= 1
                else:
                    ret.append(trip2[j])
                    p = p2[i][j]
                    j -= 1
            ret.reverse()
            return ret

    def generateLLF(self): # EDF with Maximize Slack Time
        routes = []
        L = self.makeL() # early deadline sorting

        for r in L:
            jSlack = []
            if r < 0 : continue
            j, l = 0, len(routes)
            while j < l :
                route = routes[j]
                mutab = True
                for rr in route: # checking available
                    if self.CT[abs(r)-1][abs(rr)-1] < 0:
                        mutab = False
                        break
                if mutab: # Mutually available
                    temp = route + [r, -r]
                    tript = self.subL(temp)
                    ableS = self.ableS(tript)
                    if ableS[0] :
                        jSlack.append((j, ableS[1]))
                j += 1

            if len(jSlack) < 1:
                if len(routes) < self.shutN : # there are empty shuttle
                    ntrip = [r, -r]
                    if self.ableS(ntrip)[0] :
                        routes.append(ntrip)

            else : # available, So find Maximum Slack Trip
                jSlack.sort(key = lambda js : -js[1])
                j = jSlack[0][0]
                route = routes[j]
                temp = route + [r, -r]
                tript = self.subL(temp)

                routes[j] = tript[:]
        # optimize
        self.optimize(routes)
        return Chromosome(self.Reqs.reqN, routes)

    def ableS(self, tript):
        slack = 0
        loc = self.depot
        trip = tript[:]
        t = 0

        for i in range(len(trip)) :
            dest = trip[i]
            destSta = self.requests[abs(dest) - 1][((abs(dest) - dest) // abs(dest)) + 1]
            destTime = self.requests[abs(dest) - 1][(abs(dest) - dest) // abs(dest)]

            # shuttle arrived next destination
            if i== 0 : t += self.MG.getLocDist(loc, destSta)
            else :
                depa = trip[i-1]
                depaSta = self.requests[abs(depa) - 1][((abs(depa) - depa) // abs(depa)) + 1]
                t += self.dists[depaSta][destSta]

            if dest > 0:  # pick up
                if destTime >= t : # arrive early : waiting
                    slack += (destTime - t) # slack time
                    t = destTime
                # else : arrive late / don't care

            elif dest < 0:  # drop off
                if destTime < t : # shuttle late for drop off
                    return [False, 0]
                else : # shuttle not late / don't care
                    slack += (destTime - t)
        return [True, slack/t]

    def optimize(self, trips0):
        trips = copy.deepcopy(trips0)
        idx = 0
        l = len(trips)
        while idx < l :
            mark = []
            trip = trips[idx]
            for r in trip :
                if r < 0 : continue
                jdx = 0
                while jdx < l :
                    if jdx == idx :
                        jdx += 1
                        continue
                    ntrip = self.r1i1(trips[jdx], r)
                    if ntrip == trips[jdx] :
                        jdx += 1
                        continue # r1i1 is failed
                    else :
                        trips[jdx] = copy.deepcopy(ntrip)
                        mark += [r, -r]
                        break

            if len(mark) == len(trip) : # all trip are merged
                trips = trips[:idx] + trips[idx+1:]
                tripsO = copy.deepcopy(trips)
                l = len(trips)
            else :
                trips = copy.deepcopy(trips0)
                idx += 1

    def r1i1(self, trip, x):
        tripi = trip[:]
        tx = self.requests[x - 1][0]
        tnx = self.requests[x - 1][2]

        idx = 0
        while idx < len(tripi): # insert 'x' to trip
            r = tripi[idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if t > tx:
                tripi = tripi[:idx] + [x] + tripi[idx:]
                break
            idx += 1
        if idx == len(tripi):
            tripi = tripi[:] + [x]

        idx = len(tripi)-1
        while idx > -1: # insert '-x' to trip
            r = tripi[(len(tripi)-1)-idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if tnx > t:
                tripi = tripi[:idx] + [-x] + tripi[idx:]
                break
            idx -= 1
        # add selected request to trip1

        if self.ableS(tripi)[0]:
            return tripi
        else : return trip