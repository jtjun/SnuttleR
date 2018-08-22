from Schedule import Schedule
from Shuttle import Shuttle
import math
import random
import copy


class DataGenerator:
    def __init__(self, MG, RG):
        self.MG = MG
        self.dists = MG.dists
        self.depot = MG.depot
        self.distdepot = MG.distdepot
        self.requests = RG.requests
        self.m = len(self.dists)  # number of stations
        self.n = len(self.requests)  # number of requests
        self.T = RG.T

        requests = list(enumerate(self.requests))
        self.L = self.makeL(requests)
        self.CT = self.conflictTable()  # C , index = Rn -1 (start with 0)
        self.LT = self.leastTable()
        pass

    def __str__(self):
        ret = ""
        return ret

    def conflictTable(self):
        l = len(self.requests)
        ct = []  # conflict table
        # -1 : conflict // 0 : i == j // 1 : available
        for i in range(l):
            ct.append([])
            for j in range(l):
                if i == j:
                    ct[i].append(0)
                else:
                    trip = self.subL(self.L, [i + 1, j + 1])
                    if self.available(trip): ct[i].append(1)
                    else: ct[i].append(-1)
        return ct

    def leastTable(self):
        INF = 1000000000
        l = len(self.requests)
        ct = []  # conflict table
        # -1 : conflict // 0 : i == j // 1 : available
        for i in range(l):
            ct.append([])
            for j in range(l):
                if i == j:
                    ct[i].append(0)
                else:
                    trips= [[i+1, -(i+1), j+1, -(j+1)], \
                            [i+1, j+1, -(i+1), -(j+1)], \
                            [j+1, i+1, -(i+1), -(j+1)], \
                            [j+1, -(j+1), i+1, -(i+1)], \
                            [j+1, i+1, -(j+1), -(i+1)], \
                            [i+1, j+1, -(j+1), -(i+1)]]
                    trindx = copy.deepcopy(trips)
                    trips.sort(key = lambda trip : self.costTrip(trip))
                    if self.costTrip(trips[0]) != INF :
                        ct[i].append(trindx.index(trips[0])+1)
                    else: ct[i].append(-1)
        return ct

    def costTrip(self, trip):
        INF, l , slack = 1000000000, 0, 0
        ts = []
        stas = []
        for i in trip:
            ia = abs(i)
            ts.append(self.requests[ia - 1][(ia - i) // ia])
            stas.append(self.requests[ia - 1][((ia - i) // ia) + 1])
            l += 1

        ats = [ts[0]]  # arrival times
        i = 0
        while i < l - 1:
            d = self.dists[stas[i]][stas[i + 1]]
            at = ats[i] + d  # arrival time

            if trip[i + 1] < 0:  # drop off
                if ts[i + 1] < at:
                    return INF  # arrival late so fail
                else:
                    ats.append(at)

            if trip[i + 1] > 0:  # pick up
                if ts[i + 1] > at:
                    slack += ts[i+1] - at
                    ats.append(ts[i + 1])  # arrival earlier
                # can calculate slack time at here
                else:
                    ats.append(at)
            i += 1

        return ats[len(ats)-1] - ats[0] - slack

    def serviceAble(self, schedule):
        tripSet = []
        for shuttle in schedule.shuttles:
            if not self.shuttleAble(shuttle):
                return False
            tripSet += shuttle.trip

        for i in range(len(self.requests)):
            i = i + 1
            if i not in tripSet:
                print("there are no %d in trips" % i)
                return False
            if -i not in tripSet:
                print("there are no %d in trips" % -i)
                return False
            if tripSet.count(i) != 1:
                print("there are more %d s in trips" % i)
                return False
            if tripSet.count(-i) != 1:
                print("there are more %d s in trips" % -i)
                return False
        return True

    def available(self, trip):
        ts = []
        stas = []
        l = 0
        for i in trip:
            ia = abs(i)
            ts.append(self.requests[ia - 1][(ia - i) // ia])
            stas.append(self.requests[ia - 1][((ia - i) // ia) + 1])
            l += 1

        ats = [ts[0]]  # arrival times
        i = 0
        while i < l - 1:
            d = self.dists[stas[i]][stas[i + 1]]
            at = ats[i] + d  # arrival time

            if trip[i + 1] < 0:  # drop off
                if ts[i + 1] < at:
                    return False  # arrival late
                else:
                    ats.append(at)

            if trip[i + 1] > 0:  # pick up
                if ts[i + 1] > at:
                    ats.append(ts[i + 1])  # arrival earlier
                # can calculate slack time at here
                else:
                    ats.append(at)
            i += 1

        return True

    def checkAble(self, shuttle):
        trip = shuttle.before + shuttle.trip
        nshuttle = Shuttle(self.depot, trip, [], 0)
        return self.shuttleAble(nshuttle)

    def shuttleAble(self, shuttle):
        loc = shuttle.loc
        trip = shuttle.trip[:]
        t = shuttle.t + 0

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
                    t = destTime
                # else : arrive late / don't care

            elif dest < 0:  # drop off
                if destTime < t : # shuttle late for drop off
                    return False
                # else : shuttle not late / don't care
        return True

    def getCost(self, schedule):
        COST_SHUTTLE = 1000
        cost = COST_SHUTTLE * len(schedule.shuttles)
        INF = 10000000
        if not self.serviceAble(schedule):
            return INF

        for shuttle in schedule.shuttles:
            trip = shuttle.troip
            l = len(trip)
            for i in range(l - 1):
                if trip[i] > 0:
                    staS = self.requests[trip[i] - 1][1]
                else:
                    staS = self.requests[-trip[i] - 1][3]

                if trip[i + 1] > 0:
                    staD = self.requests[trip[i + 1] - 1][1]
                else:
                    staD = self.requests[-trip[i + 1] - 1][3]

                cost += self.dists[staS][staD]
            cost += self.distdepot[self.requests[trip[0] - 1][1]] + self.distdepot[self.requests[-trip[-1] - 1][3]]
        return cost

    def generateEDF(self, schedule, t):
        already = []
        for shuttle in schedule.shuttles :
            already += shuttle.trip + shuttle.before

        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req : ((req[0]+1) not in already) and (req[1][4] <= t), reqs))
        # request[0] = number of request
        # request[1] = (timeS, stationS, timeD, stationD, timeO)

        routes = copy.deepcopy(schedule.shuttles)

        L = self.makeL(requests) # early deadline sorting
        for r in L:
            if r < 0 : continue
            j, l = 0, len(routes)
            random.shuffle(routes)
            while j < l :
                shuttle = routes[j]
                route = shuttle.trip
                mutab = True
                for rr in route: # checking available
                    if self.CT[abs(r)-1][abs(rr)-1] < 0:
                        mutab = False
                        break
                if mutab: # Mutually available
                    temp = route + [r, -r]
                    tript = self.subL(self.L, temp)
                    nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                    if self.shuttleAble(nshuttle) :
                        routes[j] = nshuttle
                        if r in schedule.rejects :
                            schedule.rejects.remove(r)
                        break # available shuttle
                j += 1

            if j == l:
                shuttle = Shuttle(self.depot, [r, -r], [], t)
                if self.shuttleAble(shuttle) :
                    routes.append(shuttle)
                    if r in schedule.rejects:
                        schedule.rejects.remove(r)
                elif r not in schedule.rejects :
                    schedule.rejects.append(r)
                    # print('Temporary reject the request {}'.format(i))

        # optimize
        self.optimize(routes)
        return Schedule(routes, schedule.rejects)

    def makeL(self, requests):
        L = []
        for req in requests :
            r = req[0]+1
            L += [r, -r]
        L.sort(key=lambda r: self.requests[abs(r) - 1][(abs(r) - r) // abs(r)])
        return L

    def subL(self, L, lst):
        trip = []
        for k in L:
            if k in lst: trip.append(k)
        return trip

    def optimize(self, shuttlesO):
        shuttles = copy.deepcopy(shuttlesO)
        idx = 0
        l = len(shuttles)
        while idx < l :
            mark = []
            shuttle = shuttles[idx]
            if len(shuttle.before) > 0 :
                idx += 1 # shuttle.before is nonempty
                continue

            for r in shuttle.trip :
                if r < 0 : continue
                jdx = 0
                while jdx < l :
                    if jdx == idx :
                        jdx += 1
                        continue
                    ntrip = self.r1i1(shuttles[jdx], r)
                    if ntrip == shuttles[jdx].trip :
                        jdx += 1
                        continue # r1i1 is failed
                    else :
                        shuttles[jdx].trip = copy.deepcopy(ntrip)
                        mark += [r, -r]
                        break

            if len(mark) == len(shuttle.trip) : # all trip are merged
                shuttles = shuttles[:idx] + shuttles[idx+1:]
                shuttlesO = copy.deepcopy(shuttles)
                l = len(shuttles)
            else :
                shuttles = copy.deepcopy(shuttlesO)
                idx += 1

    def r1i1(self, shuttle, x):
        tripi = shuttle.trip[:]
        tx = self.requests[x - 1][0]
        tnx = self.requests[x - 1][2]

        idx = 0  # insert 'x' to trip
        while idx < len(tripi):
            r = tripi[idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if t > tx:
                tripi = tripi[:idx] + [x] + tripi[idx:]
                break
            idx += 1
        idx = 0  # insert '-x' to trip
        while idx < len(tripi):
            r = tripi[(len(tripi)-1)-idx]
            t = self.requests[abs(r) - 1][(abs(r) - r) // abs(r)]
            if tnx > t:
                tripi = tripi[:idx] + [-x] + tripi[idx:]
                break
            idx += 1
        # add selected request to trip1

        shuttlei = Shuttle(shuttle.loc, tripi, shuttle.before, shuttle.t)
        if self.shuttleAble(shuttlei):
            return tripi
        else : return shuttle.trip

    def generateLLF(self, schedule, t):
        already = []
        for shuttle in schedule.shuttles:
            already += shuttle.trip + shuttle.before

        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req: ((req[0] + 1) not in already) and (req[1][4] <= t), reqs))
        # request[0] = number of request
        # request[1] = (timeS, stationS, timeD, stationD, timeO)

        routes = copy.deepcopy(schedule.shuttles)

        L = self.makeL(requests)  # early deadline sorting
        for r in L:
            if r < 0: continue
            j, l = 0, len(routes)
            random.shuffle(routes)
            while j < l:
                shuttle = routes[j]
                route = shuttle.trip
                mutab = True
                rrange = [0,len(route)-1]
                nrange = [0,len(route)-1]
                for rr in route:  # checking available
                    idx= self.LT[abs(r) - 1][abs(rr) - 1]
                    if  idx < 0:
                        mutab = False
                        break
                    else :
                        self.rRange(rrange, nrange, rr, idx-1, route)
                if mutab:  # Mutually available
                    # print(rrange, nrange, len(route))
                    ri, nri = min(rrange), max(nrange)
                    if nri < ri : ri = nri
                    tript = route[:ri] + [r] + route[ri:nri] + [-r] + route[nri:]
                    nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                    if self.shuttleAble(nshuttle):
                        routes[j] = nshuttle
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)
                        break  # available shuttle
                j += 1

            if j == l:
                shuttle = Shuttle(self.depot, [r, -r], [], t)
                if self.shuttleAble(shuttle):
                    routes.append(shuttle)
                    if r in schedule.rejects:
                        schedule.rejects.remove(r)
                elif r not in schedule.rejects:
                    schedule.rejects.append(r)
                    # print('Temporary reject the request {}'.format(i))

        # optimize
        self.optimize(routes)
        return Schedule(routes, schedule.rejects)

    def rRange(self, rrange, nrange, rr, idx, route):
        rr = abs(rr)
        if rr in route : ridx = route.index(rr)
        else : ridx = 0
        if -rr in route : nridx = route.index(-rr)
        else : nridx = 0
        if idx == 0:
            if rrange[1] > ridx : rrange[1] = ridx
            if nrange[1] > ridx : nrange[1] = ridx
        if idx == 1:
            if rrange[1] > ridx: rrange[1] = ridx
            if nrange[0] < ridx: nrange[0] = ridx
            if nrange[1] > nridx: nrange[1] = nridx
        if idx == 2:
            if rrange[0] < ridx: rrange[0] = ridx
            if rrange[1] > nridx: rrange[1] = nridx
            if nrange[0] < ridx: nrange[0] = ridx
            if nrange[1] > nridx: nrange[1] = nridx
        if idx == 3:
            if rrange[0] < nridx: rrange[0] = nridx
            if nrange[0] < nridx: nrange[0] = nridx
        if idx == 4:
            if rrange[0] < ridx: rrange[0] = ridx
            if rrange[1] > nridx: rrange[1] = nridx
            if nrange[0] < nridx: nrange[0] = nridx
        if idx == 5:
            if rrange[1] > ridx: rrange[1] = ridx
            if nrange[0] < nridx: nrange[0] = nridx
