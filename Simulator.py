from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Schedule import Schedule
from Shuttle import Shuttle
import copy


class Simulator:
    # as time goes by simulate situation
    def __init__(self, m = 20, n = 70, T = 1000, MapType = 'clust', ReqType = 'CS2'):
        self.m = m  # number of stations
        self.n = n  # number of requests
        self.T = T  # running time

        self.MG = MapGenerator(self.m, 'nomal')
        self.RG = RequestGenerator(self.MG, 'AR', self.n, self.T)
        self.DG = DataGenerator(self.MG, self.RG)
        self.requests = self.RG.requests[:]

        print(self.MG)
        print(self.RG)
        pass

    def __str__(self):
        ret = ""
        return ret

    def __main__(self): # when call the main, new schedule is generated
        requests = self.requests[:]
        schedule = Schedule([])

        # initialize schedule
        requestsT = list(filter(lambda r: r[4] < 0, requests))
        schedule = self.DG.generateEDF(schedule, 0)

        late = []
        # time is ticking
        for t in range(1, self.T) :
            # print('{t}\n{s}\n___________________\n'.format(t=t, s=schedule))
            # moving shuttles
            for shuttle in schedule.shuttles :
                if len(shuttle.trip) <= 0 :
                    shuttle.moveTo(self.MG.depot, t)
                    continue
                dest = shuttle.trip[0]
                destSta = self.requests[abs(dest) - 1][((abs(dest) - dest) // abs(dest))+1]
                destTime = self.requests[abs(dest) - 1][(abs(dest) - dest) // abs(dest)]

                sta = self.MG.stations[destSta]
                shuttle.moveTo(sta, t) # moving shuttle to the next destination

                if dest > 0 : # pick up
                    # if destTime > t : customer not arrived yet, waiting
                    if destTime <= t : # customer arrived
                        if shuttle.loc == sta : # shuttle arrived
                            shuttle.before.append(dest)
                            shuttle.trip = shuttle.trip[1:]
                        # else : shuttle not arrived yet

                elif dest < 0 : # drop off
                    if destTime < t : # shuttle late for drop off
                        if dest not in late :
                            # print('shuttle late for drop off', dest)
                            late.append(dest)
                    if destTime >= t : # shuttle not late
                        if shuttle.loc == sta : # shuttle arrived well
                            shuttle.before.append(dest)
                            shuttle.trip = shuttle.trip[1:]
                        # else : shuttle not arrived yet

                else : # dest == 0 : error
                    print("ERROR : Requests is ZERO")
                    return False

            # checking there are any new requests
            requestsTemp = list(filter(lambda r: r[4] < t, requests))
            if len(requestsT) < len(requestsTemp):
                requestsT = requestsTemp
            else: continue  # there are no new requests

            # online processing if there are new requests
            for shuttle in schedule.shuttles :
                shuttle.trip = self.haveToGo(shuttle)[:]
                # now all shuttles has only '-r'
            schedule = self.DG.generateEDF(schedule, t)

        # time ticking is done
        self.late = late
        self.report(schedule)

    def haveToGo(self, shuttle) :
        ntrip = []
        for r in shuttle.before :
            if -r not in shuttle.before:
                if r < 0 :
                    print('ERROR : trip has -r but not r')
                    print(shuttle.before, shuttle.trip)
                    return [self.n+1]
                else : ntrip.append(-r)
        if len(shuttle.before) == 0 :
            if len(shuttle.trip) > 0 :
                ntrip += [shuttle.trip[0], -shuttle.trip[0]]
        return ntrip

    def report(self, schedule):
        print('_______schedule______')
        print(len(schedule.shuttles))
        for shuttle in schedule.shuttles :
            print(shuttle.before, shuttle.trip, self.DG.checkAble(shuttle))
        print('_____________________\n')

        serviced = schedule.getServiced()
        serviced.sort()
        print(serviced)

        non =[]
        for i in range(-70, 0):
            if i not in serviced : non.append(i)
        for j in range(1, 71):
            if j not in serviced : non.append(i)
        print(non)

        dupl = []
        for i in serviced :
            if i in non :
                dupl.append(i)
        print(dupl)
        print(self.late)
        print(schedule.rejects)

        print(len(serviced), len(non), len(dupl), len(self.late), len(schedule.rejects))

if __name__ == "__main__":
    n = 1
    S = Simulator()
    for i in range(n) :
        St = copy.deepcopy(S)
        St.__main__()