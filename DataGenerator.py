from Schedule import Schedule
from Shuttle import Shuttle
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

        self.Ngene = 250
        self.Sgene = 20
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

    def available(self, trip):
        ts, stas, l, i = [], [], 0, 0
        for i in trip:
            ia = abs(i)
            ts.append(self.requests[ia - 1][(ia - i) // ia])
            stas.append(self.requests[ia - 1][((ia - i) // ia) + 1])
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
                else : # shuttle not late / don't care
                    slack += (destTime - t)

        if t == t0 : t0 -= 1
        return [True, slack/(t-t0)]

    def getCost(self, schedule):
        totSlack = self.n
        reqs = schedule.rejects[:]
        for shuttle in schedule.shuttles :
            travle = (shuttle.before + shuttle.trip)
            for r in travle :
                ar = abs(r)
                if travle.index(ar) >= travle.index(-ar):
                    return 2.0 * self.n
            reqs += travle

            ableS = self.shuttleAbleS(shuttle)
            if not ableS[0] :
                return 2.0*self.n
            totSlack += ableS[1]

        for r in reqs :
            if reqs.count(r) != 1 : return 2.0*self.n + 0.01*abs(r)

        return len(schedule.rejects) + self.n/totSlack

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

    def optimize(self, shuttlesO, shutT):
        shuttles = copy.deepcopy(shuttlesO)
        idx, l = 0, len(shuttles)
        success = False
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

            if len(mark) == len(shuttle.trip) :
                success = True # all trip are merged
                shuttles = shuttles[:idx] + shuttles[idx+1:]
                shuttlesO = copy.deepcopy(shuttles)
                l = len(shuttles)
            else :
                shuttles = copy.deepcopy(shuttlesO)
                idx += 1
        return success

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

    def insert2(self, shuttle, x, shutT):
        tripi = shuttle.trip[:]
        # add selected request to trip1
        position = []
        for xidx in range(len(tripi)) :
            for nxidx in range(len(tripi)):
                if nxidx < xidx : continue

                temp = tripi[:xidx] + [x] + tripi[xidx:nxidx] + [-x] + tripi[nxidx:]
                nshuttle = Shuttle(shuttle.loc, temp, shuttle.before[:], shutT)
                ableS = self.shuttleAbleS(nshuttle)
                if ableS[0] : # available trip
                    position.append((temp[:], ableS[1]))

        if len(position) < 1 :
            return shuttle.trip

        position.sort(key = lambda ps : -ps[1])
        return position[0][0]

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
    def generateEDF(self, schedule, t, off=False, opt = False):
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
        if opt :
            self.optimize(routes, t)
            for r in schedule.rejects:
                for i in range(len(routes)):
                    k = self.mergeTrips(routes[i].trip, [r, -r])
                    if k != None:
                        routes[i].trip = k[:]
                        break
        return Schedule(routes, schedule.rejects)

    # _______________________LLF_________________________
    def generateLLF(self, schedule, t, off=False, opt = False): # EDF with Maximize Slack Time
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
        if opt :
            self.optimize(routes, t)
            for r in schedule.rejects:
                for i in range(len(routes)):
                    k = self.mergeTrips(routes[i].trip, [r, -r])
                    if k != None:
                        routes[i].trip = k[:]
                        break
        return Schedule(routes, schedule.rejects)

    # _______________________GA_________________________
    def generateGA(self, schedule, t, off=False, opt = False): # Genetic Algorithm
        if t==0 :
            gaSchedule = self.GAOP(self.Ngene, self.Sgene)
            return gaSchedule

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
                shuttle = routes[j]
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
        if opt :
            self.optimize(routes, t)
            for r in schedule.rejects:
                for i in range(len(routes)):
                    k = self.mergeTrips(routes[i].trip, [r, -r])
                    if k != None:
                        routes[i].trip = k[:]
                        break
        return Schedule(routes, schedule.rejects)


    def GAOP(self, Ngene = 1000, Sgene = 20):
        genes = []
        costs = []

        dumy = Schedule([]) # initialize
        genes.append(self.generateLLF(dumy, 0))
        for i in range(Sgene-1):
            genes.append(self.generateEDF(dumy, 0))

        for i in range(Sgene, Ngene):
            i1 = random.randrange(Sgene)
            i2 = random.randrange(Sgene)
            genes.append(genes[i1].crossover(genes[i2]))

        genes.sort(key=lambda gene: self.getCost(gene))
        init = copy.deepcopy(genes[0])
        costs.append(self.getCost(genes[0]))

        Nstep = self.gaN  # the number of steps of evolution
        INF = 2.0*self.n
        if costs[0] >= INF:
            print("initial is shit!")

        else:
            print('{} : initial'.format(len(genes[0].rejects)))
            for i in range(Nstep):
                best = copy.deepcopy(genes[0])
                print("step {idx} is running".format(idx=i + 1))
                genes = genes[:Sgene]

                # Crossover
                for j in range(Sgene, Ngene):
                    i1 = random.randrange(Sgene)
                    i2 = random.randrange(Sgene)
                    genes.append(genes[i1].crossover(genes[i2]))

                # Mutation
                for j in range(Sgene, Ngene):
                    if random.random() < 0.1:
                        i1 = random.randrange(self.n) + 1
                        i2 = self.getSimilarRequest(i1 - 1) + 1
                        genes[j].mutation(i1, i2)

                # Optimization
                for j in range(Sgene, Ngene):
                    self.optimize(genes[j].shuttles, 0)

                    for r in genes[j].rejects:
                        for idx in range(len(genes[j].shuttles)):
                            k = self.mergeTrips(genes[j].shuttles[idx].trip, [r, -r])
                            if k != None:
                                genes[j].shuttles[idx].trip = k[:]
                                break

                genes.sort(key=lambda gene: self.getCost(gene))
                for j in range(Ngene - 1, 3, -1):
                    if genes[j] == genes[j - 4]:
                        if len(genes) <= Sgene:
                            break
                        del genes[j]

                costs.append(self.getCost(genes[0]))
                if (costs[i] > costs[i + 1]):
                    print("{}% improved | {}".format((1 - (costs[i + 1] / costs[i])) * 100, len(genes[0].rejects)))
                if costs[i+1] >= INF :
                    for i in range(Sgene) :
                        genes[i] = self.generateEDF(dumy, 0)
                    genes[0] = copy.deepcopy(best)
                    print('Detact : GA ERROR -> fix state')

                # when better than the norm, stop generating
                if (len(genes[0].rejects) <= 0):
                    print("better than norm {}".format(len(genes[0].rejects)))
                    break

        print("\nresults.....")
        for i in range(len(costs)):
            if i in [1, 2, 3]:
                pri = ["st", "nd", "rd"]
                print("{cost} {n} {w}".format(cost=costs[i], n=i, w=pri[i - 1]))
            else:
                print("%f %d th" % (costs[i], i))
        print("{}% improved".format((1 - (costs[len(costs) - 1] / costs[0])) * 100))
        print('\nInit: ')
        print(init)
        print('\nResult : ')
        print(genes[0])

        return genes[0]

    def getSimilarRequest(self, requestidx):
        t = random.random()
        for i in range(self.n):
            if t < self.ST[requestidx][i]:
                return i
            else:
                t -= self.ST[requestidx][i]
        return self.n - 1