import random
import math

tdis = 145
class RequestGenerator() :
    # requests : locations and time windows of requests
    # tuple of 5 integers : (timeS, stationS, timeD, stationD, timeO)
    # request[4] = timeO := Time that request is occur < timeS
    # n : the number of requests
    # T : the maximum time of the simulation
    def __init__(self, MG, typ = 'AR', n = 1000, T = 1440):
        self.n = n
        self.T = T

        self.Map = MG
        self.m = MG.m
        self.dists = MG.dists

        self.requests = []
        if(typ == 'AR') :
            self.requests = self.rand()
        elif(typ == 'CM') :
            self.request = self.camel()
        elif(typ == 'EX') :
            self.request = self.exp()
        elif(typ == 'UN') :
            self.requests = self.uni()
        elif(typ == 'CS') :
            self.requests = self.cluster()
        elif(typ == 'CS2'):
            self.requests = self.cluster2(0.8)
        else :
            print("ERROR : Requests Type Unavailable")
        pass

    def __str__(self):
        ret = ""
        ret += "The number of requests : {n}\n".format(n=len(self.requests))
        for request in self.requests: ret += "{r}\n".format(r=request)
        ret += "------------------------------------\n"
        return ret

    def rand(self):
        lst = []
        for i in range(self.n):
            # new version without using loop
            sta0 = random.randrange(self.m)
            sta1 = (sta0 + random.randrange(1, self.m)) % self.m
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (
                        1 + random.random())  # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.T - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0: tO = 0
            else : tO = random.randrange(0, td)
            lst.append((t0, sta0, t1, sta1, tO))
            # To ensure two stations, times are different
        return lst

    def camel(self):
        t1, t2 = self.T/3, 2*self.T/3
        lst = []
        return lst

    def exp(self, t1 = 1):
        lst = []
        return lst

    def uni(self):
        lst = []
        return lst

    def cluster(self):
        lst = []
        for i in range(self.n//2):
            # new version without using loop
            sta0 = random.randrange(self.m//2)
            sta1 = (sta0 + random.randrange(1, self.m//2)) % (self.m//2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.T - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0: tO = 0
            else: tO = random.randrange(0, td)
            lst.append((t0, sta0, t1, sta1, tO))
            
        for i in range(self.n//2, self.n):
            # new version without using loop
            sta0 = random.randrange(self.m//2) + (self.m//2)
            sta1 = (sta0 + random.randrange(1, self.m//2)) % (self.m//2) + (self.m//2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.T - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0: tO = 0
            else : tO = random.randrange(0, td)
            lst.append((t0, sta0, t1, sta1, tO))
        return lst

    def cluster2(self, p):
        np = int(self.n*p)
        RG = RequestGenerator(self.Map, 'CS', np, self.T)
        requests1 = RG.requests
        requests2 = []

        for i in range(np, self.n) :
            sta0 = random.randrange(self.m // 2) + (self.m // 2)*(i%2)
            sta1 = (sta0 + random.randrange(1, self.m // 2)) % (self.m // 2) + (self.m // 2)*((i+1)%2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.T - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0: tO = 0
            else : tO = random.randrange(0, td)
            requests2.append((t0, sta0, t1, sta1, tO))

        return requests1+requests2

