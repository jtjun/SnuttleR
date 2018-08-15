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
        self.CT = self.conflictTable()  # == C , index = Rn -1 (start with 0)
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
            already += shuttle.trip[:]

        serviced = schedule.getServiced()
        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req : (req[1][4] <= t) \
                               and ((req[0]+1) not in serviced) \
                               and ((req[0]+1) not in already), reqs))
        # request[0] = number of request
        # request[1] = (timeS, stationS, timeD, stationD, timeO)

        routes = []
        for shuttle in schedule.shuttles :
            routes.append(copy.deepcopy(shuttle))

        L = self.makeL(requests) # early deadline sorting
        for i in L:
            if i > 0:
                k, l = 0, len(routes)
                rand = list(range(l))
                random.shuffle(rand)
                while k < l :
                    j = rand[k]
                    route = routes[j].trip
                    mutab = True
                    for r in route: # checking available
                        if self.CT[abs(i) - 1][abs(r) - 1] < 0:
                            mutab = False
                            break
                    if mutab: # Mutually available
                        temp = route[:]
                        temp += [i, -i]
                        tript = self.subL(self.L, temp)
                        shuttle = Shuttle(routes[j].loc, tript, routes[j].before, t)
                        if self.shuttleAble(shuttle) :
                            routes[j] = shuttle
                            break # available shuttle
                    k += 1
                if k == l:
                    shuttle = Shuttle(self.depot, [i, -i], [], t)
                    if self.shuttleAble(shuttle) : routes.append(shuttle)
                    elif i not in schedule.rejects :
                        schedule.rejects.append(i)
                        # print('Temporary reject the request {}'.format(i))

                # optimize
                # self.optimize(routes)
                # for "shuttle.before is empty"
                # and "merge able to other shuttle"
        return Schedule(routes)

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
            if abs(k) in lst: trip.append(k)
        return trip

    def optimize(self, shuttles):
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
                        continue
                    # r1i1 is failed
                    else :
                        shuttles[jdx].trip = copy.deepcopy(ntrip)
                        mark += [r, -r]
                        break

            if len(mark) == len(shuttle.trip) : # all trip are merged
                shuttles = shuttles[:idx] + shuttles[idx+1:]
                l = len(shuttles)
            else : idx += 1

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
