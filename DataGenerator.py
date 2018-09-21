from Schedule import Schedule
from Shuttle import Shuttle
from Chromosome import Chromosome
import random
import copy


class DataGenerator:
    def __init__(self, MG, RG, shutN, gaN):
        self.MG = MG
        self.dists = MG.dists
        self.depot = MG.depot
        self.distdepot = MG.distdepot
        self.requests = RG.requests
        self.m = len(self.dists)  # number of stations
        self.n = len(self.requests)  # number of requests
        self.T = RG.T
        self.shutN = shutN
        self.gaN = gaN

        requests = list(enumerate(self.requests))
        self.L = self.makeL(requests)
        self.CT = self.conflictTable()  # C , index = Rn -1 (start with 0)
        self.ST = RG.ST

        self.Ngene = 500
        self.Sgene = 20

        reqs = list(range(1, self.n+1))
        self.offRs = list(filter(lambda req : self.requests[req-1][4] == 0, reqs))
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
                    if self.availableCT(trip): ct[i].append(1)
                    else: ct[i].append(-1)
        return ct

    def chromoAble(self, chromo):
        trips = chromo.trips
        tripSet = []

        for trip in trips:
            if not self.available(trip) : return False
            tripSet += trip

        for i in range(self.n):
            i += 1
            if tripSet.count(i) > 1:
                print("there are more %d s in trips" % i)
                return False
            if tripSet.count(-i) > 1:
                print("there are more %d s in trips" % -i)
                return False
        return True

    def availableCT(self, trip):
        ts, stas, l, i = [], [], 0, 0
        for r in trip:
            ra = abs(r)
            ts.append(self.requests[ra - 1][(ra - r) // ra])
            stas.append(self.requests[ra - 1][((ra - r) // ra) + 1])
            l += 1

        ats = [ts[0]]  # arrival times
        while i < l - 1:
            d = self.dists[stas[i]][stas[i + 1]]
            at = ats[i] + d  # arrival time

            if trip[i + 1] > 0:  # pick up
                if ts[i + 1] > at: ats.append(ts[i + 1])  # arrival earlier
                # can calculate slack time at here
                else: ats.append(at)

            if trip[i + 1] < 0:  # drop off
                if ts[i + 1] < at: return False  # arrival late
                else: ats.append(at)

            i += 1
        return True

    def available(self, trip):
        shut = Shuttle(self.depot, trip, [], 0)
        return self.shuttleAbleS(shut)[0]

    def checkAble(self, shuttle):
        trip = shuttle.before + shuttle.trip
        nshuttle = Shuttle(self.depot, trip, [], 0)
        return self.shuttleAbleS(nshuttle)[0]

    def shuttleAbleS(self, shuttle):
        slack = 0
        loc = shuttle.loc
        trip = shuttle.trip[:]
        for r in trip :
            if trip.count(r) != 1 : return [False, 0]
        t = shuttle.t + 0
        t0 = t

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
                # else : # shuttle not late / don't care

        if t == t0 : t0 -= 1
        return [True, slack/(t-t0)]

    def getCost(self, schedule):
        # 2.0*n : impossible Shuttle
        # 1.0 : index_r > index_-r
        # 0.01 : duplicate
        totSlack = self.n
        reqs = schedule.rejects[:]
        for shuttle in schedule.shuttles :
            travle = (shuttle.before + shuttle.trip)
            for r in travle :
                ar = abs(r)
                if travle.index(ar) >= travle.index(-ar):
                    return 2.0*self.n + ar
            reqs += travle

            ableS = self.shuttleAbleS(shuttle)
            if not ableS[0] :
                return 2.0*self.n
            totSlack += ableS[1]

        for r in reqs :
            if reqs.count(r) != 1 : return 2.0*self.n + 0.01*abs(r)

        return len(schedule.rejects) + self.n/totSlack

    def getCostGA(self, chromo):
        if not self.chromoAble(chromo):
            return 2.0 * chromo.reqN

        sk = chromo.reqN
        for trip in chromo.trips:
            ts = []
            stas = []
            l = 0
            for i in trip:
                ia = abs(i)
                ts.append(self.requests[ia - 1][(ia - i) // ia])
                stas.append(self.requests[ia - 1][((ia - i) // ia) + 1])
                l += 1

            ats = [ts[0]]

            for i in range(l - 1):
                d = self.dists[stas[i]][stas[i + 1]]
                at = ats[i] + d

                if trip[i + 1] < 0:
                    if ts[i + 1] < at:
                        return  2.0 * chromo.reqN
                        # not available trip
                    else:
                        ats.append(at)

                if trip[i + 1] > 0:
                    if ts[i + 1] > at:
                        sk += (ts[i + 1] - at) / self.T
                        ats.append(ts[i + 1])
                    else:
                        ats.append(at)

        return len(chromo.rejects) + chromo.reqN / sk

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

    def getSimilarRequest(self, requestidx):
        t = random.random()
        for i in range(self.n):
            if t < self.ST[requestidx][i]:
                return i
            else:
                t -= self.ST[requestidx][i]
        return self.n - 1

    def optimize(self, shuttles0, shutT):
        shuttlesO = copy.deepcopy(shuttles0)
        shuttles = copy.deepcopy(shuttles0)
        idx, l = 0, len(shuttles)
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
                    ntrip = self.insert(shuttles[jdx], r, shutT)
                    if ntrip == shuttles[jdx].trip :
                        jdx += 1
                        continue # insert is failed
                    else :
                        shuttles[jdx].trip = copy.deepcopy(ntrip)
                        shuttle.trip.remove(r)
                        shuttle.trip.remove(-r)
                        mark += [r, -r]
                        break

            if len(mark) == len(shuttle.trip) : # all trip are merged
                shuttles = shuttles[:idx] + shuttles[idx+1:]
                shuttlesO = copy.deepcopy(shuttles)
                l = len(shuttles)
            else :
                shuttles = copy.deepcopy(shuttlesO)
                idx += 1
        return copy.deepcopy(shuttles)

    def insert(self, shuttle, x, shutT):
        tripi = shuttle.trip[:]
        # add selected request to trip1
        temp = self.mergeTrips(tripi, [x, -x])
        if temp == None :
            return shuttle.trip

        nshuttle = Shuttle(shuttle.loc, temp, shuttle.before[:], shutT)
        ableS = self.shuttleAbleS(nshuttle)
        if ableS[0]:
            return temp
        return shuttle.trip

    def mergeTrips(self, trip1, trip2):
        mint1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        mint2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p1 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]
        p2 = [[-1] * (len(trip2) + 1) for i in range(len(trip1) + 1)]

        mint1[0][0] = 0
        mint2[0][0] = 0
        trip1 = [0] + trip1
        trip2 = [0] + trip2
        for i in range(len(trip1)):  # the number of requests done in trip1
            for j in range(len(trip2)):  # the number of requests done in trip2
                if i == 0:
                    sta1 = 0
                else:
                    if trip1[i] > 0:
                        sta1 = self.requests[trip1[i] - 1][1]
                    else:
                        sta1 = self.requests[-trip1[i] - 1][3]

                    if i == 1:
                        sta1p = 0
                    else:
                        if trip1[i - 1] > 0:
                            sta1p = self.requests[trip1[i - 1] - 1][1]
                        else:
                            sta1p = self.requests[-trip1[i - 1] - 1][3]

                if j == 0:
                    sta2 = 0
                else:
                    if trip2[j] > 0:
                        sta2 = self.requests[trip2[j] - 1][1]
                    else:
                        sta2 = self.requests[-trip2[j] - 1][3]

                    if j == 1:
                        sta2p = 0
                    else:
                        if trip2[j - 1] > 0:
                            sta2p = self.requests[trip2[j - 1] - 1][1]
                        else:
                            sta2p = self.requests[-trip2[j - 1] - 1][3]

                if i > 0:
                    if mint1[i - 1][j] != -1 and (
                            mint1[i][j] == -1 or mint1[i][j] > mint1[i - 1][j] + self.dists[sta1p][sta1]):
                        mint1[i][j] = mint1[i - 1][j] + self.dists[sta1p][sta1]
                        p1[i][j] = 1
                    if mint2[i - 1][j] != -1 and (
                            mint1[i][j] == -1 or mint1[i][j] > mint2[i - 1][j] + self.dists[sta2][sta1]):
                        mint1[i][j] = mint2[i - 1][j] + self.dists[sta2][sta1]
                        p1[i][j] = 2

                    if trip1[i] > 0:
                        if mint1[i][j] != -1 and mint1[i][j] < self.requests[trip1[i] - 1][0]:
                            mint1[i][j] = self.requests[trip1[i] - 1][0]
                    if trip1[i] < 0:
                        if mint1[i][j] != -1 and mint1[i][j] > self.requests[-trip1[i] - 1][2]:
                            mint1[i][j] = -1

                if j > 0:
                    if mint1[i][j - 1] != -1 and (
                            mint2[i][j] == -1 or mint2[i][j] > mint1[i][j - 1] + self.dists[sta1][sta2]):
                        mint2[i][j] = mint1[i][j - 1] + self.dists[sta1][sta2]
                        p2[i][j] = 1
                    if mint2[i][j - 1] != -1 and (
                            mint2[i][j] == -1 or mint2[i][j] > mint2[i][j - 1] + self.dists[sta2p][sta2]):
                        mint2[i][j] = mint2[i][j - 1] + self.dists[sta2p][sta2]
                        p2[i][j] = 2

                    if trip2[j] > 0:
                        if mint2[i][j] != -1 and mint2[i][j] < self.requests[trip2[j] - 1][0]:
                            mint2[i][j] = self.requests[trip2[j] - 1][0]
                    if trip2[j] < 0:
                        if mint2[i][j] != -1 and mint2[i][j] > self.requests[-trip2[j] - 1][2]:
                            mint2[i][j] = -1

        if mint1[-1][-1] == -1 and mint2[-1][-1] == -1:
            # print("Merge Trips Failed")
            return None
        else:
            ret, p = [], 0
            i = len(trip1) - 1
            j = len(trip2) - 1
            if mint1[-1][-1] == -1: p = 2
            elif mint2[-1][-1] == -1: p = 1
            elif mint1[-1][-1] < mint2[-1][-1]: p = 1
            else: p = 2

            while i > 0 or j > 0:
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


    #_______________________EDF_________________________
    def generateEDF(self, schedule, t, off=False):
        already = []
        for shuttle in schedule.shuttles :
            already += shuttle.trip + shuttle.before

        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req : ((req[0]+1) not in already) and (req[1][4] <= t), reqs))
        if off : requests = reqs

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
                    if self.shuttleAbleS(nshuttle)[0] :
                        routes[j] = nshuttle
                        if r in schedule.rejects :
                            schedule.rejects.remove(r)
                        break # available shuttle
                j += 1

            if j == l:
                if len(routes) >= self.shutN :
                    if r not in schedule.rejects :
                        schedule.rejects.append(r)
                else : # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0] :
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)
                    elif r not in schedule.rejects :
                        schedule.rejects.append(r)

        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    # _______________________LLF_________________________
    def generateLLF(self, schedule, t, off=False): # EDF with Maximize Slack Time
        already = []
        for shuttle in schedule.shuttles :
            already += shuttle.trip + shuttle.before

        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req : ((req[0]+1) not in already) and (req[1][4] <= t), reqs))
        if off : requests = reqs

        routes = copy.deepcopy(schedule.shuttles)
        L = self.makeL(requests) # early deadline sorting
        for r in L:
            jSlack = []
            if r < 0 : continue
            j, l = 0, len(routes)
            while j < l :
                shuttle = routes[j]
                route = shuttle.trip
                mutab = True
                for rr in route: # checking available
                    if self.CT[abs(r)-1][abs(rr)-1] < 0:
                        mutab = False
                        break
                if mutab: # Mutually available
                    tript = self.subL(self.L, route + [r, -r])
                    nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                    ableS = self.shuttleAbleS(nshuttle)
                    if ableS[0] :
                        jSlack.append((j, ableS[1]))
                j += 1

            if len(jSlack) < 1:
                if len(routes) >= self.shutN :
                    if r not in schedule.rejects :
                        schedule.rejects.append(r)
                else : # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0] :
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)
                    elif r not in schedule.rejects :
                        schedule.rejects.append(r)

            else : # available, So find Maximum Slack Trip
                jSlack.sort(key = lambda js : -js[1])
                j = jSlack[0][0]
                shuttle = routes[j]
                route = shuttle.trip
                tript = self.subL(self.L, route + [r, -r])

                nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                routes[j] = nshuttle

                if r in schedule.rejects:
                    schedule.rejects.remove(r)

        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    # _______________________GA_________________________
    def generateGA(self, schedule, t, off=False): # Genetic Algorithm
        # GA operating is already done, respect previous schedule
        already = []
        for shuttle in schedule.shuttles:
            already += (shuttle.trip + shuttle.before)

        reqs = list(enumerate(self.requests[:]))
        requests = list(filter(lambda req: ((req[0] + 1) not in already) and (req[1][4] <= t), reqs))
        if off : requests = reqs
        # request[0] = number of request
        # request[1] = (timeS, stationS, timeD, stationD, timeO)

        routes = copy.deepcopy(schedule.shuttles)

        L = self.makeL(requests)  # early deadline sorting
        for r in L:
            jSlack = []
            if r < 0: continue
            j, l = 0, len(routes)
            while j < l:
                shuttle = routes[j] # different from LLF
                tript = self.insert(shuttle, r, t)

                if shuttle.trip != tript:  # insert available
                    nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                    ableS = self.shuttleAbleS(nshuttle)
                    if ableS[0]:
                        jSlack.append((j, ableS[1]))
                j += 1

            if len(jSlack) < 1:
                if len(routes) >= self.shutN:
                    if r not in schedule.rejects:
                        schedule.rejects.append(r)
                else:  # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0]:
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)
                    elif r not in schedule.rejects:
                        schedule.rejects.append(r)

            else:  # available, So find Maximum Slack Trip
                jSlack.sort(key=lambda js: -js[1])
                j = jSlack[0][0]
                shuttle = routes[j]
                tript = self.insert(shuttle, r, t)

                nshuttle = Shuttle(shuttle.loc, tript, shuttle.before[:], t)
                routes[j] = nshuttle

                if r in schedule.rejects:
                    schedule.rejects.remove(r)

        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    def localOpt(self, routes, t, rejects):
        routes = self.optimize(routes, t)
        schedule = Schedule(routes, rejects)
        for r in schedule.rejects:
            for i in range(len(schedule.shuttles)):
                k = self.insert(schedule.shuttles[i], r, t)
                if k != schedule.shuttles[i].trip:
                    schedule.shuttles[i].trip = k[:]
                    break

        schedule = Schedule(schedule.shuttles[:], schedule.rejects[:])
        idx = 0
        while len(schedule.shuttles) < self.shutN:
            if idx >= len(schedule.rejects): break
            r = schedule.rejects[idx]
            shuttle = Shuttle(self.depot, [r, -r], [], t)
            if self.shuttleAbleS(shuttle)[0]:
                schedule.shuttles.append(shuttle)
            idx += 1

        return Schedule(schedule.shuttles[:], schedule.rejects[:])