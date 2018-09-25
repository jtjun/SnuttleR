import math
import random

class MapGenerator:
    # staN : the number of stations
    # stations : locations of stations [tuple of 2 real numbers and name (x, y, name)] == map info
    # dists : matrix which has the distance info
    # typ : type of map
    # upp : upper bound processing trigger

    # */ we have to change road : from euclid to x,y axis

    def __init__(self, staN = 20, typ = 'clust', upp = False):
        self.staN = staN
        self.stations = []

        if typ == 'nomal' :
            for j in range(self.staN) :
                sta = (random.random()*100, random.random()*100, j)
                while sta in self.stations :
                    sta = (random.random() * 100, random.random() * 100, j)
                self.stations.append(sta)
            # To ensure all stations are different

        elif typ == 'clust' :
            for j in range(self.staN//2):
                sta = (random.random() * 30, random.random() * 30, j)
                self.stations.append(sta)
            # To ensure all stations are different

            for j in range(self.staN//2, self.staN):
                sta = (random.random() * 30 + 70, random.random() * 30 + 70, j)
                self.stations.append(sta)

        else :
            print("ERROR : Map type doesn't exist")
            pass

        self.depot = (50, 50, -1)
        self.distdepot = []
        for j in range(self.staN):
            self.distdepot.append(math.sqrt((self.stations[j][0]-self.depot[0])**2
                                            +(self.stations[j][1]-self.depot[1])**2))

        self.dists = self.getDists()
        if upp : self.upper() # all dist be synchronized whit tick
        pass

    def __str__(self):
        ret = ""
        ret += "The number of stations : {m}\n".format(m = self.staN)
        ret += "Depot: {c}\n".format(c = self.depot)
        for coord in self.stations: ret += "{c}\n".format(c = coord)
        ret += "------------------------------------\n"
        return ret

    def getDists(self):
        m = self.staN # number of sta
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

    def upper(self):
        for distt in self.dists :
            i = 0
            while i < len(distt) :
                distt[i] = math.ceil(distt[i])
                i += 1
        j =0
        while j < len(self.distdepot) :
            self.distdepot[j] = math.ceil(self.distdepot[j])
            j += 1