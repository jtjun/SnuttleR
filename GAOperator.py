from DataGenerator import DataGenerator
from Chromosome import Chromosome
from Schedule import Schedule
import math
import random
import copy

class GAOperator:
    def __init__(self, DG, initial, normR, ns = 25, offP = 0.5, off = False):
        self.genes = []
        self.costs = []
        self.normR = normR
        self.On = int(DG.n - DG.n*offP)

        Ngene = 1000 # the number of genes
        Nggene = 20 # the number of genes which can survive

        dumy = Schedule([])
        if initial == 'EDF':
            for i in range(Nggene):
                trips = []
                schedule = DG.generateEDF(dumy, 0, off)
                for shuttle in schedule.shuttles :
                    trips.append(shuttle.trip)
                self.genes.append(Chromosome(DG.n, trips))

        elif initial == 'LLF':
            for i in range(Nggene):
                trips = []
                schedule = DG.generateLLF(dumy, 0, off)
                for shuttle in schedule.shuttles :
                    trips.append(shuttle.trip)
                self.genes.append(Chromosome(DG.n, trips))

        
        for i in range(Nggene, Ngene):
            i1 = random.randrange(Nggene)
            i2 = random.randrange(Nggene)
            self.genes.append(self.genes[i1].crossover(self.genes[i2]))

        self.genes.sort(key = lambda gene : DG.getCostGA(gene))
        self.costs.append(DG.getCostGA(self.genes[0]))
        self.init = copy.deepcopy(self.genes[0])

        Nstep = ns # the number of steps of evolution
        INF = 10000000

        if self.costs[0] >= INF:
            print("initial is shit!")

        else :
            print('{} : initial'.format(len(self.genes[0].rejects)-self.On))
            for i in range(Nstep):

                print("step {idx} is running".format(idx = i+1))

                self.genes = self.genes[:Nggene]

                # Crossover
                for j in range(Nggene, Ngene):
                    i1 = random.randrange(Nggene)
                    i2 = random.randrange(Nggene)
                    self.genes.append(self.genes[i1].crossover(self.genes[i2]))

                # Mutation
                for j in range(Nggene, Ngene):
                    if random.random() < 0.1:
                        i1 = random.randrange(DG.n) + 1
                        # i2 = random.randrange(DG.m) + 1
                        i2 = DG.getSimilarRequest(i1 - 1) + 1
                        self.genes[j].mutation(i1, i2)

                # Optimization
                for j in range(Ngene):
                    if DG.getCostGA(self.genes[j]) < INF:
                        self.genes[j] = self.optimize(self.genes[j], DG)

                self.genes.sort(key = lambda gene : DG.getCostGA(gene))

                for j in range(Ngene-1, 3, -1):
                    if self.genes[j] == self.genes[j-4]:
                        if len(self.genes) <= Nggene:
                            break
                        del self.genes[j]
                self.costs.append(DG.getCostGA(self.genes[0]))
                if(self.costs[i] > self.costs[i+1]) :
                    print("{}% improved | {}".format((1-(self.costs[i+1]/self.costs[i]))*100, len(self.genes[0].rejects)-self.On))

                    # when better than the norm, stop generating
                if(len(self.genes[0].rejects)-self.On <= self.normR) :
                    print("better than norm".format(len(self.genes[0].rejects)-self.On))
                    break

        print("\nresults.....")
        for i in range(len(self.costs)):
            if i in [1, 2, 3] :
                pri = ["st", "nd", "rd"]
                print("{cost} {n} {w}" .format(cost = self.costs[i], n =  i, w = pri[i-1]))
            else :
                print("%f %d th" %(self.costs[i], i))
        print("{}% improved".format((1-(self.costs[len(self.costs)-1]/self.costs[0]))*100))
        print('\nInit: ')
        print(self.init)
        print('\nResult : ')
        print(self.genes[0])
        pass

    def __str__(self):
        pass

    def optimize(self, chromo, DG):
        trips = copy.deepcopy(chromo.trips)
        for i in range(len(trips)-1, -1, -1):
            for j in range(i):
                k = DG.mergeTrips(trips[j], trips[i])
                if k != None:
                    trips[j] = k[:]
                    del trips[i]
                    break
        for r in chromo.rejects:
            for i in range(len(trips)):
                k = DG.mergeTrips(trips[i], [r, -r])
                if k != None:
                    trips[i] = k[:]
                    break
        return Chromosome(chromo.reqN, trips)

    def getResult(self):
        return self.genes[0].trips