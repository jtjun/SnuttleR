from Schedule import Schedule
from Shuttle import Shuttle
import random
import copy


class GAOperator:
    # genes : list of Schedule(as gene
    # costs : save lowest cost of each generation
    # gaN : the number of GA generation
    # Ngene : the size of gene pool
    # Sgene : the number of genes which can survive

    def __init__(self, DG, gaN=10, Ngene=1000, Sgene=20, off=False):
        self.genes = []
        self.costs = []
        self.gaN = gaN # the number of GA generation
        self.INF = 2.0  # regarding as cost function

        self.reqN = DG.reqN
        self.offRs = DG.offRs
        self.onRN = DG.reqN - len(self.offRs)
        self.shutN = DG.shutN

        self.geneAble = DG.geneAble
        self.depot = DG.depot
        self.localOpt = DG.localOpt
        self.mergeTrips = DG.mergeTrips
        self.getCostGA = DG.getCostGA
        self.getSimilarRequest = DG.getSimilarRequest
        self.shuttleAbleS = DG.shuttleAbleS
        self.Ngene = Ngene  # the size of gene pool
        self.Sgene = Sgene  # the number of genes which can survive


    # Operating Section
        # make initial genes___________
        dumyE = Schedule([])
        dumyL = Schedule([])

        for i in range(Sgene):
            if i == 0 : # LLF should contain at least one (why: len ==)
                schedule = DG.generateEDF(dumyE, 0, off)
                self.genes.append(schedule)
                continue
            EDF = DG.generateEDF(dumyE, 0, off)
            LLF = DG.generateLLF(dumyL, 0, off)

            if len(EDF.rejects) <= len(LLF.rejects): schedule = EDF
            else: schedule = LLF # when rejects same -> EDF (why: random)
            # select one which has smaller rejects
            self.genes.append(schedule)

        for i in range(Sgene, Ngene):
            i1 = random.randrange(Sgene)
            i2 = random.randrange(Sgene)
            self.genes.append(self.genes[i1].crossover(self.genes[i2]))

        self.genes.sort(key=lambda gene: self.getCostGA(gene))
        self.costs.append(self.getCostGA(self.genes[0]))
        self.init = copy.deepcopy(self.genes[0])
        if self.costs[0] >= self.INF: # check initial is serviceable
            print("initial is shit!")
        # initializing end___________

        else:
        # Evolution is starting___________
            print('*Processing offline requests in GA* (online : {})'.format(self.onRN))
            print('{} : initial'.format(len(self.genes[0].rejects)))
            best = copy.deepcopy(self.genes[0])
            for i in range(self.gaN):
                print("step {idx} is running".format(idx=i + 1))

                self.genes = self.genes[:Sgene]
                # cut the genes by # of survive able genes

                # Crossover___________
                for j in range(Sgene, Ngene):
                    i1 = random.randrange(Sgene)
                    i2 = random.randrange(Sgene)
                    self.genes.append(self.genes[i1].crossover(self.genes[i2]))

                # Mutation___________
                for j in range(Sgene, Ngene):
                    if random.random() < 0.30:
                        i1 = random.randrange(self.reqN) + 1
                        i2 = self.getSimilarRequest(i1 - 1) + 1
                        self.genes[j].mutation(i1, i2)

                # Optimization___________
                for j in range(Ngene):
                    if self.getCostGA(self.genes[j]) < self.INF:
                        genejOpt = self.optimize(copy.deepcopy(self.genes[j]))
                        if self.geneAble(genejOpt): self.genes[j] = genejOpt
                        genejOpt = self.optimization(copy.deepcopy(self.genes[j]))
                        if self.geneAble(genejOpt): self.genes[j] = genejOpt
                        genejOpt = self.ropti(copy.deepcopy(self.genes[j]))
                        if self.geneAble(genejOpt): self.genes[j] = genejOpt

                self.genes.sort(key=lambda gene: self.getCostGA(gene))

                for j in range(Ngene - 1, 3, -1):
                    if self.genes[j] == self.genes[j - 4]:
                        if len(self.genes) <= Sgene:
                            break
                        del self.genes[j]

                # Check best's geneAble
                if (len(best.rejects) < len(self.genes[0].rejects)):
                    self.genes[0] = copy.deepcopy(best)
                else: best = copy.deepcopy(self.genes[0])
                self.costs.append(self.getCostGA(self.genes[0]))
                # saving best's cost

                if (self.costs[i] > self.costs[i + 1]):
                    print("{}% improved | {}"\
                          .format((1 - (self.costs[i + 1] / self.costs[i])) * 100,\
                                  len(self.genes[0].rejects)))
                    # printing percentage of improvement

                # when no reject, stop generating
                if (len(self.genes[0].rejects) < 1):
                    print("WOW there are no reject!!".format(len(self.genes[0].rejects)))
                    break

    # Printing Section
        print("\nresults.....")
        for i in range(len(self.costs)):
            if i in [1, 2, 3]:
                pri = ["st", "nd", "rd"]
                print("{cost} {n} {w}".format(cost=self.costs[i], n=i, w=pri[i - 1]))
            else: print("%f %d th" % (self.costs[i], i))
        print("{}% improved".format((1 - (self.costs[len(self.costs) - 1] / self.costs[0])) * 100))

        print('\nInit: ')
        print(self.init)
        print(self.chromoAble(self.init))
        print('\nResult : ')
        print(self.genes[0])
        print(self.chromoAble(self.genes[0]))
        pass

    def __str__(self):
        pass

    def optimize(self, gene):
        shuttles = copy.deepcopy(gene.shuttles)
        for i in range(len(shuttles) - 1, -1, -1):
            for j in range(i):
                k = self.mergeTrips(shuttles[j].after,\
                                    shuttles[i].after)
                if k != None:
                    nshut = Shuttle(shuttles[j].loc, k[:])
                    shuttles[j] = nshut
                    del shuttles[i]
                    break

        for r in gene.rejects:
            for i in range(len(shuttles)):
                k = self.mergeTrips(shuttles[i].after,\
                                    [r, -r])
                if k != None:
                    nshut = Shuttle(shuttles[i].loc, k[:])
                    shuttles[i] = nshut
                    break

        return Schedule(shuttles, self.offRs)

    def optimization(self, gene):
        shuttles = copy.deepcopy(gene.shuttles)
        return self.localOpt(shuttles, 0, gene.rejects)

    def ropti(self, gene):
        shuttles = copy.deepcopy(gene.shuttles)
        for r in gene.rejects:
            for i in range(len(shuttles)):
                k = self.mergeTrips(shuttles[i].trips,\
                                    [r, -r])
                if k != None:
                    nshut = Shuttle(shuttles[i].loc, k[:])
                    shuttles[i] = nshut
                    break

        rejects = Schedule(shuttles, self.offRs).rejects
        idx = 0
        while len(shuttles) < self.shutN :
            if idx >= len(rejects) : break
            r = rejects[idx]
            shut = Shuttle(shuttles[0].loc, [r, -r])
            if self.shuttleAbleS(shut)[0] :
                shuttles.append(shut)
            idx += 1

        return Schedule(shuttles, self.offRs)

    def getResult(self):
        return self.genes[0]

    def getRejs(self):
        return self.genes[0].rejects