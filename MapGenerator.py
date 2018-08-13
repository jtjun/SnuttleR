import math
import random

class MapGenerator:
    # m : the number of stations
    # stations : locations of stations [tuple of 2 real numbers and name (x, y, name)] == map info
    # dists : matrix which has the distance info
    def __init__(self, m = 20, typ = 'nomal'):
        self.m = m
        if typ == 'nomal' :
            self.stations = []
            for j in range(self.m) :
                sta = (random.random()*100, random.random()*100, j)
                while sta in self.stations :
                    sta = (random.random() * 100, random.random() * 100, j)
                self.stations.append(sta)
            # To ensure all stations are different

        if typ == 'clust' :
            self.stations = []
            for j in range(self.m//2):
                sta = (random.random() * 30, random.random() * 30, j)
                self.stations.append(sta)
            # To ensure all stations are different

            for j in range(self.m//2, self.m):
                sta = (random.random() * 30 + 70, random.random() * 30 + 70, j)
                self.stations.append(sta)

        self.depot = (random.random()*100, random.random()*100, -1)
        self.distdepot = []
        for j in range(self.m):
            self.distdepot.append(math.sqrt((self.stations[j][0]-self.depot[0])**2+(self.stations[j][1]-self.depot[1])**2))

        self.dists = self.getDists()
        pass

    def __str__(self):
        ret = ""
        ret += "The number of stations : {m}\n".format(m = self.m)
        ret += "Depot: {c}\n".format(c = self.depot)
        for coord in self.stations: ret += "{c}\n".format(c = coord)
        ret += "------------------------------------\n"
        return ret

    def getDists(self):
        m = self.m # number of sta
        dists = [[None] * m for i in range(m)]
        for i in range(m) :
            for j in range(m) :
                d = self.getDistance(i, j)
                dists[i][j] = d
        return dists


    def getDistance(self, x, y):
        # get euclidean distance between station x and station y
        return math.sqrt((self.stations[x][0]-self.stations[y][0])**2
                         +(self.stations[x][1]-self.stations[y][1])**2)

    def getLocDist(self, loc, x):
        return math.sqrt((self.stations[x][0] - loc[0]) ** 2
                         + (self.stations[x][1] - loc[1]) ** 2)