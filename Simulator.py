from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Schedule import Schedule
from Visualization import Visualization

from GAOperator import GAOperator
from Shuttle import Shuttle

import time

class Simulator:
    # as time goes by simulate situation
    def __init__(self, m = 20, n = 100, T = 1000, shutN = 10, shutC = 5, offP = 0.6, \
                 MapType = 'clust', ReqType = 'CS2', gaN = 5, upp = False, lP = 0):
        self.m = m  # number of stations
        self.n = n  # number of requests
        self.shutN = shutN  # number of shuttles
        self.T = T  # running time
        self.shutC = shutC # capacity of shuttle
        self.offP = offP # ratio of offline requests
        self.gaN = gaN # number of GA steps
        self.upp = upp # convert dists to upper bound
        self.lP = lP # acceptable Late time Policy

        self.MG = MapGenerator(self.m, MapType, self.upp)
        self.RG = RequestGenerator(self.MG, ReqType, self.n, self.T, self.offP)
        self.DG = DataGenerator(self.MG, self.RG, self.shutN, self.gaN, self.lP)
        self.requests = self.RG.requests[:]

        print(self.MG)
        print(self.RG)
        print('Stations : {m} | Requests : {r} | Shuttles : {s}\nTime : {t} | Off proportion : {o} | Capacity : {c}\n'\
              .format(m=self.m, r=self.n, s=self.shutN, t=self.T, o=self.offP, c=self.shutC))
        print('------------------------------------')
        self.rDS = self.RG.rDS()

        self.times = []
        pass

    def __str__(self):
        ret = ""
        return ret

    def GAINIT(self, off):
        onlR = int(self.n*(1-self.offP))
        GAOP = GAOperator(self.DG, 0, onlR, self.gaN, off)
        trips = GAOP.getResult()
        rejs = GAOP.getRejs()
        shuttles =[]
        for trip in trips:
            shuttle = Shuttle(self.MG.depot, trip, [], 0)
            shuttles.append(shuttle)
        return Schedule(shuttles, rejs)

    def __main__(self, numm, typ, off): # when call the main, new schedule is generated
        startT = time.time()
        requests = self.requests[:]
        schedule = Schedule([])
        late = []
        self.late = late

        if off :
            if typ == 'EDF' : schedule = self.DG.generateEDF(schedule, 0, True)
            if typ == 'MSF': schedule = self.DG.generateMSF(schedule, 0, True)
            if typ == 'LLF' : schedule = self.DG.generateLLF(schedule, 0, True)
            if typ == 'GA' : schedule = self.GAINIT(True)
            self.report(schedule, typ + ' off ' + str(numm))
            return [len(schedule.rejects), 0]

        # initialize schedule
        requestsT = list(filter(lambda r: r[4] < 0, requests))
        if typ == 'EDF' : schedule = self.DG.generateEDF(schedule, 0)
        if typ == 'MSF': schedule = self.DG.generateMSF(schedule, 0)
        if typ == 'LLF' : schedule = self.DG.generateLLF(schedule, 0)
        if typ == 'GA' : schedule = self.GAINIT(False)
        inRjs = len(schedule.rejects)
        print("{}'s initial {}".format(typ, inRjs))

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
                            custN = shuttle.getCustN()
                            if custN >= self.shutC :
                                print('ERROR : exceed the shuttle capacity {}'.format(custN))
                            shuttle.before.append(dest)
                            shuttle.trip = shuttle.trip[1:]
                        # else : shuttle not arrived yet

                elif dest < 0 : # drop off
                    if destTime < t : # shuttle late for drop off
                        if shuttle.loc == sta : # shuttle arrived anyway
                            shuttle.before.append(dest)
                            shuttle.trip = shuttle.trip[1:]
                            late.append(str(dest)+' late : '+str((t-destTime)))

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
            if typ in ['empty']:
                for shuttle in schedule.shuttles :
                    shuttle.trip = self.haveToGo(shuttle)[:]
                    # now all shuttles has only 'have to go'

            if typ == 'EDF': schedule = self.DG.generateEDF(schedule, t)
            if typ == 'MSF': schedule = self.DG.generateMSF(schedule, t)
            if typ == 'LLF': schedule = self.DG.generateLLF(schedule, t)
            if typ == 'GA' : schedule = self.DG.generateGA(schedule, t)

        # time ticking is done
        endT = time.time()
        self.late = late
        warring = self.report(schedule, typ+' '+str(numm))

        self.times.append(endT-startT)
        print(endT-startT)
        print("\n")

        if warring > 0 : return [self.n, inRjs]
        return [len(schedule.rejects), inRjs]

    def haveToGo(self, shuttle) :
        ntrip = []
        for r in shuttle.before :
            if -r not in shuttle.before:
                if r > 0 : ntrip.append(-r)
                else :
                    print('ERROR : trip has -r but not r')
                    print(shuttle.before, shuttle.trip)
                    return [self.n+1]

        if len(shuttle.before) == 0 :
            if len(shuttle.trip) > 0 :
                r = abs(shuttle.trip[0])
                ntrip = [r, -r]
            else :
                print('ERROR : totally empty shuttle')
        return ntrip

    def report(self, schedule, numm):
        warring = 0
        print('_______schedule______')
        print(numm)
        print(len(schedule.shuttles))
        for shuttle in schedule.shuttles :
            shutable = self.DG.checkAble(shuttle)
            print(shuttle.before, shuttle.trip, shutable)
            if not shutable :
                print("ERROR : *This Shuttle is NOT serviceable.*")
                warring += 1
        if self.DG.getCost(schedule) >= 2.0*self.n :
            print('ERROR : 0.01:duplicate / 1.0:index {}'.format(self.DG.getCost(schedule)))
            print('_____________________\n')
            return 0
        print('_____________________\n')

        serviced = schedule.getServiced(self.n)
        serviced.sort()

        non =[]
        for i in range(-self.n, self.n+1):
            if i == 0 : continue
            if i not in serviced : non.append(i)

        left = []
        for shuttle in schedule.shuttles :
            left += shuttle.trip

        print('{} serviced'.format(serviced))
        print('{} non'.format(non))
        print('{} left'.format(left))
        print('{} late'.format(self.late))

        print('shutN {} / serv {} |non {} |left {} |late {}'.format(len(schedule.shuttles), len(serviced), len(non), len(left), len(self.late)))
        print('Reject')
        print('{lr} {r}'.format(r = schedule.rejects, lr = len(schedule.rejects)))
        if warring > 0 : print("ERROR{} : There are {} Shuttles which is NOT serviceable*".format(warring, warring))

        V = Visualization()
        V.drawTrips(self.MG, self.RG, schedule, 'test '+str(numm))
        print('_____________________\n')
        return warring

    def saving(self, edf, msf, llf, ga):
        e, m, l, g = edf[0], msf[0], llf[0], ga[0]
        el = (1 - 1.0 * e / self.n) * 100
        ml = (1 - 1.0 * m / self.n) * 100
        ll = (1 - 1.0 * l / self.n) * 100
        gl = (1 - 1.0 * g / self.n) * 100

        f = open("./result/result.csv", 'a')
        f.write("\n{e},{m},{l},{g},|,{mn},{n},{o},{sn},{sc},|,{el},{ml},{ll},{gl},|init,{ei},{mi},{li},{gi},{rds}"\
                .format(e=e,m=m,l=l,g=g,\
                        mn=self.m,n=self.n,o=self.offP,sn=self.shutN,sc=self.shutC,rds=self.rDS,\
                        el=el,ml=ml,ll=ll,gl=gl,\
                        ei=edf[1],mi=msf[1],li=llf[1],gi=ga[1]))
        f.close()

    def saveTime(self):
        f = open("./result/time.csv", 'a')
        f.write("{tE},{tM},{tL},{tG}\n"\
                .format(tE=self.times[0],tM=self.times[1],tL=self.times[2],tG=self.times[3]))
        f.close()

if __name__ == "__main__":
    n = 98
    off = False
    for i in range(n) :
        S = Simulator(MapType='clust', ReqType='CS2')
        edf = S.__main__(0, 'EDF', off)
        msf = S.__main__(0, 'MSF', off)
        llf = S.__main__(0, 'LLF', off)
        ga = S.__main__(0, 'GA', off)
        S.saving(edf,msf,llf,ga)
        print('EDF : {e} | MSF : {m} | LLF : {l} | GA : {g}\n'.format(e = edf[0], m=msf[0], l=llf[0], g=ga[0]))
        print(S.times)
        S.saveTime()