from DataGenerator import DataGenerator
from Chromosome import Chromosome
import math
import random
import copy

class GAOperator:
    
    def __init__(self, DG, initial, ns = 25):
        self.genes = []
        self.costs = []

        Ngene = 1000 # the number of genes
        Nggene = 20 # the number of genes which can survive


        if initial == 'RAND':
            for i in range(Nggene):
                self.genes.append(DG.generateRAND())
        elif initial == 'OTOC':
            for i in range(Nggene):
                self.genes.append(DG.generateOTOC())
        elif initial == 'CFSS':
            for i in range(Nggene):
                self.genes.append(DG.generateCFSS())

        
        for i in range(Nggene, Ngene):
            i1 = random.randrange(Nggene)
            i2 = random.randrange(Nggene)
            self.genes.append(self.genes[i1].crossover(self.genes[i2]))

        self.genes.sort(key = lambda gene : DG.getCost(gene))
        self.costs.append(DG.getCost(self.genes[0]))
        self.init = copy.deepcopy(self.genes[0])

        Nstep = ns # the number of steps of evolution
        INF = 10000000

        if self.costs[0] >= INF:
            print("initial is shit!")

        else :
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
                        i1 = random.randrange(DG.Reqs.reqN) + 1
                        # i2 = random.randrange(DG.m) + 1
                        i2 = DG.getSimilarRequest(i1 - 1) + 1
                        self.genes[j].mutation(i1, i2)

                # Optimization
                for j in range(Ngene):
                    if DG.getCost(self.genes[j]) < INF:
                        self.genes[j] = self.optimize(self.genes[j], DG)
                        # self.genes[j] = self.opt(self.genes[j], DG)
                        # self.genes[j] = self.rem1ins1(self.genes[j], DG, DG.n)

                self.genes.sort(key = lambda gene : DG.getCost(gene))

                for j in range(Ngene-1, 3, -1):
                    if self.genes[j] == self.genes[j-4]:
                        if len(self.genes) <= Nggene:
                            break
                        del self.genes[j]
                self.costs.append(DG.getCost(self.genes[0]))
                if(self.costs[i] > self.costs[i+1]) :
                    print("{}% improved".format((1-(self.costs[i+1]/self.costs[i]))*100))
                    # norm = (0.7078 * math.sqrt(2 * (DG.Reqs.reqN + len(self.genes[0].trips))) + 0.551) * 100
                    # if(self.costs[i+1] <= norm) :
                    #     print("reach lower bound of tsp {}".format(norm))
                    #     break

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

    def opt(self, chromo, DG):
        trips = copy.deepcopy(chromo.trips)
        trips = DG.divideinto(trips)
        return Chromosome(chromo.reqN, trips)

    def rem1ins1(self, chromo, DG, n):
        trips = copy.deepcopy(chromo.trips)
        for i in range(n) :
            trips = DG.r1i1(trips, 1)
        return Chromosome(chromo.reqN, trips)
