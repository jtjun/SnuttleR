from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Schedule import Schedule
from Visualization import Visualization

from GAOperator import GAOperator
from Shuttle import Shuttle

class Simulator:
    # as time goes by simulate situation
    def __init__(self, staN = 20, reqN = 100, runT = 1000, shutN = 10, shutC = 5, offP = 0.6, \
                 MapType = 'clust', ReqType = 'CS2', gaN = 5, Ngene = 1000, Sgene = 20, upp = False, lateP = 0):
        self.staN = staN  # number of stations
        self.reqN = reqN  # number of requests
        self.runT = runT  # running time
        self.shutN = shutN  # number of shuttles
        self.shutC = shutC # capacity of shuttle
        self.offP = offP # ratio of offline requests
        self.gaN = gaN # number of GA steps
        self.Ngene = Ngene # the size of gene pool
        self.Sgene = Sgene  # the number of genes which will survive
        self.upp = upp # convert dists to upper bound
        self.lateP = lateP # acceptable Late time Policy

        self.MG = MapGenerator(self.staN, MapType, self.upp)
        self.RG = RequestGenerator(self.MG, ReqType, self.reqN, self.runT, self.offP)
        self.DG = DataGenerator(self.MG, self.RG, self.shutN, self.lateP)
        self.requests = self.RG.requests[:]

        print(self.MG)
        print(self.RG)
        print('Stations : {m} | Requests : {r} | Shuttles : {s}\nTime : {t} | Off proportion : {o} | Capacity : {c}\n'\
              .format(m=self.staN, r=self.reqN, s=self.shutN, t=self.runT, o=self.offP, c=self.shutC))
        print('------------------------------------')
        self.rDS = self.RG.rDS()
        pass

    def __str__(self):
        ret = ""
        return ret

    def GAINIT(self, off):
        GAOP = GAOperator(self.DG, self.gaN, self.Ngene, self.Sgene, off)
        return GAOP.getResult()

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
            return [len(schedule.rejects), 0]

        # initialize schedule
        requestsT = list(filter(lambda r: r[4] < 0, requests))
        if typ == 'EDF' : schedule = self.DG.generateEDF(schedule, 0)
        if typ == 'LLF' : schedule = self.DG.generateLLF(schedule, 0)
        if typ == 'GA' : schedule = self.GAINIT(False)
        inRjs = len(schedule.rejects)
        print("{}'s initial {}".format(typ, inRjs))

        # time is ticking
        for t in range(1, self.runT) :
            # print('{t}\n{s}\n___________________\n'.format(t=t, s=schedule))
            # moving shuttles
            for shuttle in schedule.shuttles :
                if len(shuttle.after) <= 0 :
                    shuttle.moveTo(self.MG.depot, t)
                    continue
                dest = shuttle.after[0]
                destSta = self.requests[abs(dest) - 1][((abs(dest) - dest) // abs(dest))+1]
                destTime = self.requests[abs(dest) - 1][(abs(dest) - dest) // abs(dest)]

                sta = self.MG.stations[destSta]
                shuttle.moveTo(sta, t) # moving shuttle to the next destination

                if dest > 0 : # pick up
                    # if destTime > t : customer not arrived yet, waiting
                    if destTime <= t : # customer arrived
                        if shuttle.loc == sta : # shuttle arrived
                            custN = shuttle.getCustomN()
                            if custN >= self.shutC :
                                print('ERROR : exceed the shuttle capacity {}'.format(custN))
                                return False
                            shuttle.before.append(dest)
                            shuttle.after = shuttle.after[1:]
                        # else : shuttle not arrived yet

                elif dest < 0 : # drop off
                    if shuttle.loc == sta:  # shuttle arrived
                        shuttle.before.append(dest)
                        shuttle.after = shuttle.after[1:]

                        if destTime < t : # shuttle late for drop off
                            late.append(str(dest)+' late : '+str((t-destTime)))
                        # else : // destTime >= t shuttle not late

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
            if typ == 'EDF': schedule = self.DG.generateEDF(schedule, t)
            elif typ == 'LLF': schedule = self.DG.generateLLF(schedule, t)
            elif typ == 'GA' : schedule = self.DG.generateGA(schedule, t)
            else : print('ERROR : Simulator type error')

        # time ticking is done
        self.late = late
        warring = self.report(schedule, typ+' '+str(numm))
        if warring > 0 : return [self.reqN, inRjs]
        return [len(schedule.rejects), inRjs]

    def report(self, schedule, numm):
        warring = 0
        print('_______schedule______')
        print(numm)
        print(len(schedule.shuttles))
        for shuttle in schedule.shuttles :
            shutable = self.DG.checkAble(shuttle)
            print(shuttle.before, shuttle.after, shutable)
            if not shutable :
                print("ERROR : *This Shuttle is NOT serviceable.*")
                warring += 1
        if not self.DG.geneAble(schedule) :
            print('ERROR : {} (0.01:duplicate / 1.0:index)'.format(self.DG.getCost(schedule)))
            print('_____________________\n')
            #return 0
        print('_____________________\n')

        serviced = schedule.getServiced(self.reqN)
        serviced.sort()

        non =[]
        for i in range(-self.reqN, self.reqN+1):
            if i == 0 : continue
            if i not in serviced : non.append(i)

        left = []
        for shuttle in schedule.shuttles :
            left += shuttle.after

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

    def saving(self, edf, llf, ga):
        e, l, g = edf[0], llf[0], ga[0]
        el = (1 - 1.0 * e / self.reqN) * 100
        ll = (1 - 1.0 * l / self.reqN) * 100
        gl = (1 - 1.0 * g / self.reqN) * 100

        f = open("./result/result.csv", 'a')
        f.write("\n{e},{l},{g},|,{m},{n},{o},{sn},{sc},|,{el},{ll},{gl},|init,{ei},{li},{gi},{rds}"\
                .format(e=e,l=l,g=g,\
                        m=self.staN,n=self.reqN,o=self.offP,sn=self.shutN,sc=self.shutC,rds=self.rDS,\
                        el=el,ll=ll,gl=gl,ei=edf[1],li=llf[1],gi=ga[1]))
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
        print('EDF : {e} ({ei}) | LLF : {l} ({li}) | GA : {g} ({gi})\n'\
              .format(e = edf[0], ei = edf[1], l=llf[0], li = llf[1], g=ga[0], gi=ga[1]))