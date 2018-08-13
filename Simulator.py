from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Visualization import Visualization
from Chromosome import Chromosome
from GAOperator import GAOperator

def main():
    INF = 10000000
    m, n, T = 20, 70, 1000
    mtyp = 'clust'
    rtyp = 'CS2'

    ns = 10

    MAP = MapGenerator(m=m, typ = mtyp)
    Reqs = RequestGenerator(Map = MAP, typ = rtyp, n = n, T = T)
    DG = DataGenerator(MG = MAP, RG = Reqs)
    cfss = DG.generateCFSS() # for available map test

    while DG.getCost(cfss) == INF :
        print('Regenerating..')
        MAP = MapGenerator(m=m, typ=mtyp)
        Reqs = RequestGenerator(Map=MAP, typ=rtyp, n=n, T=T)
        DG = DataGenerator(MG=MAP, RG=Reqs)
        cfss = DG.generateCFSS() # for available map test
    print('------------------------------------')

    print(MAP)
    print(Reqs)
    GAOP = GAOperator(DG, 'CFSS', ns)

def Repoprt(MAP, Reqs, DG, GAOP) :
    V = Visualization()
    V.drawPoints([coord[0] for coord in MAP.stations], [coord[1] for coord in MAP.stations], 'stations', 'ro')

    V.drawPoints(range(len(GAOP.costs)), GAOP.costs, 'costs for each generation', 'r-')

    unavoid = 0

    for request in Reqs.requests:
        unavoid += MAP.dists[request[1]][request[3]]

    print("unavoid: {d}".format(d = unavoid))

    print("INIT: {c}".format(c = DG.getCost(GAOP.init) - unavoid))
    print("FINAL: {c}".format(c = DG.getCost(GAOP.genes[0]) - unavoid))
    print("{}% improved".format(100*(1-((DG.getCost(GAOP.genes[0]) - unavoid))/(DG.getCost(GAOP.init) - unavoid))))

    print(GAOP.init);

    for (i, trip) in enumerate(GAOP.init.trips):
        points = []
        for request in trip:
            if request > 0:
                points.append(MAP.stations[Reqs.requests[request-1][1]][0:2])
            else:
                points.append(MAP.stations[Reqs.requests[-request-1][3]][0:2])
        V.drawPoints([p[0] for p in points], [p[1] for p in points], 'routes/init/stations of shuttle {i}'.format(i = i), 'r-')

    print(GAOP.genes[0]);

    for (i, trip) in enumerate(GAOP.genes[0].trips):
        points = []
        for request in trip:
            if request > 0:
                points.append(MAP.stations[Reqs.requests[request-1][1]][0:2])
            else:
                points.append(MAP.stations[Reqs.requests[-request-1][3]][0:2])
        V.drawPoints([p[0] for p in points], [p[1] for p in points], 'routes/final/stations of shuttle {i}'.format(i = i), 'r-')
    pass

    V.drawTrips(MAP, Reqs, GAOP.init, 'init')
    V.drawTrips(MAP, Reqs, GAOP.genes[0], 'final')

if __name__ == "__main__": # execute when python Simulator.py executed
    main()
    # print(Chromosome.generateRandomly(10,3))