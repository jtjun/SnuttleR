from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Schedule import Schedule
from Visualization import Visualization

from GAOperator import GAOperator
from Shuttle import Shuttle

class Simulator:
    # as time goes by simulate situation
    def __init__(self, m = 20, n = 100, T = 1000, shutN = 10, shutC = 5, offP = 0.6, \
                 MapType = 'clust', ReqType = 'CS2', gaN = 9, upp = True):
        self.m = m  # number of stations
        self.n = n  # number of requests
        self.shutN = shutN  # number of shuttles
        self.T = T  # running time
        self.shutC = shutC # capacity of shuttle
        self.offP = offP # ratio of offline requests
        self.gaN = gaN # number of GA steps

        self.MG = MapGenerator(self.m, MapType, upp)
        self.RG = RequestGenerator(self.MG, ReqType, self.n, self.T, self.offP)
        self.DG = DataGenerator(self.MG, self.RG, shutN, gaN)
        self.requests = self.RG.requests[:]

        print(self.MG)
        print(self.RG)
        print('Stations : {m} | Requests : {r} | Shuttles : {s}\nTime : {t} | Off proportion : {o} | Capacity : {c}\n'\
              .format(m=self.m, r=self.n, s=self.shutN, t=self.T, o=self.offP, c=self.shutC))
        pass

    def __str__(self):
        ret = ""
        return ret

    def GAINIT(self, off):
        onlR = int(self.n*(1-self.offP))
        GAOP = GAOperator(self.DG, 0, onlR, self.gaN, off)
        trips = GAOP.getResult()
        shuttles =[]
        for trip in trips:
            shuttle = Shuttle(self.MG.depot, trip, [], 0)
            shuttles.append(shuttle)
        return Schedule(shuttles)

    def __main__(self, numm, typ, off): # when call the main, new schedule is generated
        requests = self.requests[:]
        schedule = Schedule([])
        late = []
        self.late = late

        if off :
            if typ == 'EDF' : schedule = self.DG.generateEDF(schedule, 0, True)
            if typ == 'LLF' : schedule = self.DG.generateLLF(schedule, 0, True)
            if typ == 'GA' : schedule = self.GAINIT(True)
            self.report(schedule, typ + ' off ' + str(numm))
            return len(schedule.rejects)

        # initialize schedule
        requestsT = list(filter(lambda r: r[4] < 0, requests))
        if typ == 'EDF' : schedule = self.DG.generateEDF(schedule, 0)
        if typ == 'LLF' : schedule = self.DG.generateLLF(schedule, 0)
        if typ == 'GA' : schedule = self.GAINIT(False)

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
            if typ in ['EDF', 'LLF']:
                for shuttle in schedule.shuttles :
                    shuttle.trip = self.haveToGo(shuttle)[:]
                    # now all shuttles has only 'have to go'

            if typ == 'EDF': schedule = self.DG.generateEDF(schedule, t)
            if typ == 'LLF': schedule = self.DG.generateLLF(schedule, t)
            if typ == 'GA' : schedule = self.DG.generateGA(schedule, t)

        # time ticking is done
        self.late = late
        self.report(schedule, typ+' '+str(numm))
        return len(schedule.rejects)

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
        print('_______schedule______')
        print(numm)
        print(len(schedule.shuttles))
        for shuttle in schedule.shuttles :
            print(shuttle.before, shuttle.trip, self.DG.checkAble(shuttle))
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

        V = Visualization()
        V.drawTrips(self.MG, self.RG, schedule, 'test '+str(numm))
        print('_____________________\n')

    def saving(self, e, l, g):
        f = open("./result/result.csv", 'a')
        el = (1-1.0*e/l)*100
        gl = (1-1.0*g/l)*100
        f.write("\n{e},{l},{g},|,{m},{n},{o},{sn},{sc},|,{el},{ll},{gl}"\
                .format(e=e,l=l,g=g,\
                        m=self.m,n=self.n,o=self.offP,sn=self.shutN,sc=self.shutC,\
                        el=el,ll=0,gl=gl))
        f.close()

if __name__ == "__main__":
    n = 1
    off = False
    for i in range(n) :
        S = Simulator(MapType='clust', ReqType='CS2')
        edf = S.__main__(0, 'EDF', off)
        llf = S.__main__(0, 'LLF', off)
        ga = S.__main__(0, 'GA', off)
        S.saving(edf,llf,ga)
        print('EDF : {e} | LLF : {l} | GA : {g}'.format(e = edf, l=llf, g=ga))