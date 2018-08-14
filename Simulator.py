from MapGenerator import MapGenerator
from RequestGenerator import RequestGenerator
from DataGenerator import DataGenerator
from Schedule import Schedule
from Shuttle import Shuttle


class Simulator:
    # as time goes by simulate situation
    def __init__(self):
        pass

    def __str__(self):
        ret = ""
        return ret

    def __main__(self):
        m = 20 # number of stations
        n = 70 # number of requests
        T = 1000 # running time

        MG = MapGenerator(m, 'clust')
        RG = RequestGenerator(MG, 'CS2', n, T)
        DG = DataGenerator(MG, RG)
        schedule = Schedule([], [])

        # initialize schedule
        schedule = DG.cfssTicking(schedule, 0)
        # time is ticking
        for t in range(T) :
            # at time = t servicing process
            serviced = schedule.serviced
            for shuttle in schedule.shuttles :
                trip = shuttle.trip

                # processing drop off
                # // code is here //
                serviced += shuttle.serviced

            # forward to the time = t+1
            schedule = DG.cfssTicking(schedule, t+1)