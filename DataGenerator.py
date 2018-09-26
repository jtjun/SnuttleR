from Schedule import Schedule
from Shuttle import Shuttle
import random
import copy


class DataGenerator:
    # MG : Map Generator
    # RG : Request Generator
    # shutN : the number of shuttle
    # lateP : acceptable late time Policy
    # L : list sorted requests by time window
    # CT : conflict table
    # ST : similar table

    def __init__(self, MG, RG, shutN,  lateP = 0):
        self.dists = MG.dists
        self.depot = MG.depot
        self.distdepot = MG.distdepot
        self.getLocDist = MG.getLocDist
        self.staN = MG.staN  # number of stations

        self.requests = RG.requests
        self.runT = RG.runT # running time of simulator
        self.reqN = RG.reqN # number of requests
        self.ST = RG.ST  # similar table
        reqs = list(range(1, self.reqN + 1))
        self.offRs = list(filter(lambda req: self.requests[req - 1][4] == 0, reqs))

        self.shutN = shutN
        self.lateP = lateP

        requests = list(enumerate(self.requests))
        self.L = self.makeL(requests)
        self.CT = self.conflictTable()  # C , index = Rn -1 (start with 0)
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

    def geneAble(self, gene):
        shuttles = gene.shuttles
        tripSet = []

        for shuttle in shuttles:
            after = shuttle.getTrip()
            nshuttle = Shuttle(self.depot, after)
            if not self.shuttleAbleS(nshuttle)[0] : return False
            tripSet += shuttle.getTrip()

        for i in range(self.reqN):
            i += 1
            if tripSet.count(i) > 1:
                #print("there are more %d s in trips" % i)
                return False
            if tripSet.count(-i) > 1:
                #print("there are more %d s in trips" % -i)
                return False
        return True

    def available(self, trip):
        shut = Shuttle(self.depot, trip, [], 0)
        return self.shuttleAbleS(shut)[0]

    def checkAble(self, shuttle):
        trip = shuttle.getTrip()
        nshuttle = Shuttle(self.depot, trip, [], 0)
        return self.shuttleAbleS(nshuttle)[0]

    def shuttleAbleS(self, shuttle):
        slack = 0 # */ check!!!
        loc = shuttle.loc
        after = shuttle.after[:]

        for r in after :
            if after.count(r) != 1 : return [False, 0]
        t = shuttle.t + 0
        t0 = t

        for i in range(len(after)) :
            dest = after[i]
            destSta = self.requests[abs(dest) - 1][((abs(dest) - dest) // abs(dest)) + 1]
            destTime = self.requests[abs(dest) - 1][(abs(dest) - dest) // abs(dest)]

            # shuttle arrived next destination
            if i== 0 : t += self.getLocDist(loc, destSta)
            else :
                depa = after[i-1]
                depaSta = self.requests[abs(depa) - 1][((abs(depa) - depa) // abs(depa)) + 1]
                t += self.dists[depaSta][destSta]

            if dest > 0:  # pick up
                if destTime >= t : # arrive early : waiting
                    slack += (destTime - t) # slack time
                    t = destTime
                # else : arrive late / don't care

            elif dest < 0:  # drop off
                if destTime < t : # shuttle late for drop off
                    late = t-destTime
                    if late > self.lateP : return [False, 0]
                    else : slack -= late
                # else : # shuttle not late / don't care

        if t == t0 : t0 -= 1
        return [True, slack/(t-t0)]

    def getCost(self, schedule):
        # 2.0*reqN : impossible Shuttle
        # 1.0 : index_r > index_-r
        # 0.01 : duplicate
        if not self.geneAble(schedule) :
            return 2.0*self.reqN
            # not serviceable shuttle in schedule

        totSlack = self.reqN
        reqs = schedule.rejects[:]
        for shuttle in schedule.shuttles :
            travle = (shuttle.before + shuttle.getTrip())
            for r in travle :
                ar = abs(r)
                if travle.index(ar) >= travle.index(-ar):
                    # wrong order
                    return 2.0*self.reqN + ar
            reqs += travle

            ableS = self.shuttleAbleS(shuttle)
            if not ableS[0] :
                # not serviceable shuttle in schedule
                return 2.0*self.reqN
            totSlack += ableS[1]

        for r in reqs :
            if reqs.count(r) != 1 :
                # duplicate
                return 2.0*self.reqN + 0.01*abs(r)
        return len(schedule.rejects) + self.reqN/totSlack

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
        for i in range(self.reqN):
            if t < self.ST[requestidx][i]:
                return i
            else:
                t -= self.ST[requestidx][i]
        return self.reqN - 1

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

            for r in shuttle.after :
                if r < 0 : continue
                jdx = 0
                while jdx < l :
                    if jdx == idx :
                        jdx += 1
                        continue
                    ntrip = self.insert(shuttles[jdx], r, shutT)
                    if ntrip == shuttles[jdx].after :
                        jdx += 1
                        continue # insert is failed
                    else :
                        # insert r to shuttle j
                        shuttles[jdx].after = copy.deepcopy(ntrip)
                        shuttle.after.remove(r)

                        # remove r from shuttle i
                        shuttle.after.remove(-r)
                        mark += [r, -r]
                        break

            if len(mark) == len(shuttle.after) : # all trip are merged
                shuttles = shuttles[:idx] + shuttles[idx+1:]
                shuttlesO = copy.deepcopy(shuttles)
                l = len(shuttles)

            else :
                shuttles = copy.deepcopy(shuttlesO)
                idx += 1

        return copy.deepcopy(shuttles)

    def insert(self, shuttle, x, shutT):
        afteri = shuttle.after[:]
        # add selected request to trip1
        temp = self.mergeTrips(afteri, [x, -x])
        if temp == None : # Merge Able
            return shuttle.after

        nshuttle = Shuttle(shuttle.loc, temp, shuttle.before[:], shutT)
        if self.shuttleAbleS(nshuttle)[0] :
            return temp # service able
        else : return shuttle.after

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
            already += shuttle.getTrip()

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
                after = shuttle.after[:]
                mutab = True

                for rr in after: # checking availability
                    if self.CT[abs(r)-1][abs(rr)-1] < 0:
                        mutab = False
                        break

                if mutab: # Mutually available
                    aftert = self.subL(self.L, after + [r, -r])
                    nshuttle = Shuttle(shuttle.loc, aftert, shuttle.before[:], t)

                    if self.shuttleAbleS(nshuttle)[0] :
                        routes[j] = nshuttle # serviceable
                        if r in schedule.rejects :
                            schedule.rejects.remove(r)
                        break # available shuttle
                    # else : check next shuttle
                j += 1

            if j == l:
                if len(routes) >= self.shutN :
                    if r not in schedule.rejects :
                        schedule.rejects.append(r)
                        # r is rejected

                else : # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0] :
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)

                    elif r not in schedule.rejects :
                        schedule.rejects.append(r)

                    # else : r is already rejected
        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    # _______________________LLF_________________________
    def generateLLF(self, schedule, t, off=False): # EDF with Maximize Slack Time
        already = []
        for shuttle in schedule.shuttles :
            already += shuttle.getTrip()

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
                after = shuttle.after[:]
                mutab = True

                for rr in after: # checking availability
                    if self.CT[abs(r)-1][abs(rr)-1] < 0:
                        mutab = False
                        break

                if mutab: # Mutually available
                    aftert = self.subL(self.L, after + [r, -r])
                    nshuttle = Shuttle(shuttle.loc, aftert, shuttle.before[:], t)

                    ableS = self.shuttleAbleS(nshuttle)
                    if ableS[0] :
                        jSlack.append((j, ableS[1]))
                    # else : check next shuttle
                j += 1

            if len(jSlack) < 1: # no available shuttle
                if len(routes) >= self.shutN :
                    if r not in schedule.rejects :
                        schedule.rejects.append(r)
                        # r is rejected

                else : # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0] :
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)

                    elif r not in schedule.rejects :
                        schedule.rejects.append(r)

                    # else : r is already rejected

            else : # available, So find Maximum Slack Trip
                jSlack.sort(key = lambda js : -js[1])
                j = jSlack[0][0] # MST's shuttle number

                shuttle = routes[j]
                aftert = self.subL(self.L, shuttle.after + [r, -r])
                nshuttle = Shuttle(shuttle.loc, aftert, shuttle.before[:], t)
                routes[j] = nshuttle

                if r in schedule.rejects:
                    schedule.rejects.remove(r)

                # else : r is not rejected before
        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    # _______________________GA_________________________
    def generateGA(self, schedule, t, off=False): # Genetic Algorithm
        # GA operating is already done, respect previous schedule
        already = []
        for shuttle in schedule.shuttles:
            already += shuttle.getTrip()

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
                aftert = self.insert(shuttle, r, t)

                if shuttle.after != aftert:  # insert available
                    nshuttle = Shuttle(shuttle.loc, aftert, shuttle.before[:], t)
                    ableS = self.shuttleAbleS(nshuttle)

                    if ableS[0]:
                        jSlack.append((j, ableS[1]))

                    # else : not serviceable
                j += 1

            if len(jSlack) < 1: # no available shuttle
                if len(routes) >= self.shutN:
                    if r not in schedule.rejects:
                        schedule.rejects.append(r)
                        # r is rejected

                else:  # there are new shuttle
                    shuttle = Shuttle(self.depot, [r, -r], [], t)
                    if self.shuttleAbleS(shuttle)[0]:
                        routes.append(shuttle)
                        if r in schedule.rejects:
                            schedule.rejects.remove(r)

                    elif r not in schedule.rejects:
                        schedule.rejects.append(r)

                    # else : r is already rejected

            else:  # available, So find Maximum Slack Trip
                jSlack.sort(key=lambda js: -js[1])
                j = jSlack[0][0]
                shuttle = routes[j]
                aftert = self.insert(shuttle, r, t)

                nshuttle = Shuttle(shuttle.loc, aftert, shuttle.before[:], t)
                routes[j] = nshuttle

                if r in schedule.rejects:
                    schedule.rejects.remove(r)

                # else : r is not rejected before
        # optimize
        return self.localOpt(routes, t, schedule.rejects)

    def localOpt(self, routes, t, rejects):
        routes = self.optimize(routes, t)
        schedule = Schedule(routes, rejects)
        for r in schedule.rejects:
            for i in range(len(schedule.shuttles)):
                temp = self.insert(schedule.shuttles[i], r, t)

                # insert r to shuttle i
                if temp != schedule.shuttles[i].after:
                    schedule.shuttles[i].after =temp[:]
                    break
                # else : insert failed

        schedule = Schedule(schedule.shuttles[:], schedule.rejects[:])
        idx = 0
        while len(schedule.shuttles) < self.shutN:
            if idx >= len(schedule.rejects): break

            r = schedule.rejects[idx]
            shuttle = Shuttle(self.depot, [r, -r], [], t)
            if self.shuttleAbleS(shuttle)[0]:
                schedule.shuttles.append(shuttle)
            # else : r is rejected
            idx += 1

        return Schedule(schedule.shuttles[:], schedule.rejects[:])