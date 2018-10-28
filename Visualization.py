import matplotlib
matplotlib.use('Agg') # because there is no display for this program
import matplotlib.pyplot as plt
import random
import numpy as np

class Visualization:
    def __init__(self):
        pass
    
    def __str__(self):
        pass

    def drawPoints(self, xs, ys, filestr, opts):
        fig = plt.figure()
        plt.subplot(111)
        plt.plot(xs, ys, opts, label = 'coords of stations')
        plt.axis([0,100,0,100])
        plt.title('Stations')
        plt.legend()

        fig.savefig(filestr+'.png')

    def drawTrips(self, MAP, Reqs, schedule, name):
        fig = plt.figure()
        plt.subplot(111)
        shutn = len(schedule.shuttles)

        for (i, shuttle) in enumerate(schedule.shuttles):
            trip = shuttle.before + shuttle.trip
            points = []
            for request in trip:
                if request > 0:
                    points.append(MAP.stations[Reqs.requests[request - 1][1]][0:2])
                else:
                    points.append(MAP.stations[Reqs.requests[-request - 1][3]][0:2])

            C = random.uniform((1.0*i)/shutn, (i+1.0)/shutn)
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            plt.plot(xs, ys, color = plt.cm.Reds(C), label = (i+1))
            plt.axis([0, 100, 0, 100])

        plt.title('Trips')
        plt.legend(loc = 'center left', bbox_to_anchor = (0.98, 0.5))
        fig.savefig('result/'+name+' Whole Trips.png')
        pass

    def drawTripsGA(self, MAP, Reqs, chromo, name):
        fig = plt.figure()
        plt.subplot(111)
        shutn = len(chromo.trips)

        for (i, trip) in enumerate(chromo.trips):
            points = []
            for request in trip:
                if request > 0:
                    points.append(MAP.stations[Reqs.requests[request - 1][1]][0:2])
                else:
                    points.append(MAP.stations[Reqs.requests[-request - 1][3]][0:2])

            C = random.uniform((1.0 * i) / shutn, (i + 1.0) / shutn)
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            plt.plot(xs, ys, color=plt.cm.Reds(C), label=(i + 1))
            plt.axis([0, 100, 0, 100])

        plt.title('Trips')
        plt.legend(loc='center left', bbox_to_anchor=(0.98, 0.25))
        fig.savefig(name + ' Whole Trips.png')
        pass