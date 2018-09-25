import random
import math
import copy

tdis = 145


class RequestGenerator():
    # MG : Map Generator
    # typ : type of requests
    # requests : locations and time windows of requests
    # tuple of 5 integers : (timeS, stationS, timeD, stationD, timeO)
    # timeO = time that request is occur < timeS (request[4])
    # reqN : the number of requests
    # runT : the running time of the simulation
    # offP : offline proportion
    # rDS : list of request's dist/timeD-timeS
    # ST : similar table for mutation

    # */ ensure all requests are serviceable !! shuttle[r, -r] is serviceable

    def __init__(self, MG, typ='CS2', reqN=100, runT=1440, offP=0.5):
        self.reqN = reqN
        self.runT = runT
        self.offRN = reqN * offP

        self.Map = MG
        self.staN = MG.staN
        self.dists = MG.dists

        self.requests = []
        if (typ == 'AR'):
            self.requests = self.rand()
        elif (typ == 'CM'):
            self.request = self.camel()
        elif (typ == 'EX'):
            self.request = self.exp()
        elif (typ == 'UN'):
            self.requests = self.uni()
        elif (typ == 'CS'):
            self.requests = self.cluster()
        elif (typ == 'CS2'):
            self.requests = self.cluster2(0.8)
        else:
            print("ERROR : Requests Type Unavailable")

        self.ST = self.similarTable()
        pass

    def __str__(self):
        offR = 0
        for r in self.requests:
            if r[4] == 0: offR += 1

        ret = ""
        ret += "The number of requests : {n} | off {off}\n".format(n=len(self.requests), off=offR)
        for request in self.requests: ret += "{r}\n".format(r=request)
        ret += "------------------------------------\n"
        return ret

    def rand(self):
        lst = []
        for i in range(self.reqN):
            req = self.makeReq()
            lst.append(req)
        return self.ensureOFF(lst)

    def makeReq(self):
        sta0 = random.randrange(self.m)
        sta1 = (sta0 + random.randrange(1, self.m)) % self.m
        # change index 1~m to 0~m-1 for easy access of dist[][]

        d = self.dists[sta0][sta1] * (1 + random.random())
        # make time interval random value between distance and 2*distance
        t0 = random.randrange(math.floor(self.runT - d))
        t1 = int(math.floor(t0 + d))
        # To ensure two stations, times are different

        td = t0 - tdis
        if td <= 0:
            tO = 0
        else:
            tO = random.randrange(0, td)

        return (t0, sta0, t1, sta1, tO)

    def camel(self):
        t1, t2 = self.runT / 3, 2 * self.runT / 3
        lst = []
        return lst

    def exp(self, t1=1):
        lst = []
        return lst

    def uni(self):
        lst = []
        return lst

    def cluster(self):
        lst = []
        for i in range(self.reqN // 2):
            sta0 = random.randrange(self.staN // 2)
            sta1 = (sta0 + random.randrange(1, self.staN // 2)) % (self.staN // 2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.runT - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0:
                tO = 0
            else:
                tO = random.randrange(0, td)
            lst.append((t0, sta0, t1, sta1, tO))

        for i in range(self.reqN // 2, self.reqN):
            sta0 = random.randrange(self.staN // 2) + (self.staN // 2)
            sta1 = (sta0 + random.randrange(1, self.staN // 2)) % (self.staN // 2) + (self.staN // 2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.runT - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0:
                tO = 0
            else:
                tO = random.randrange(0, td)
            lst.append((t0, sta0, t1, sta1, tO))
        # separate map into 2 area
        return self.ensureOFF(lst)

    def cluster2(self, p):
        np = int(self.reqN * p)
        RG = RequestGenerator(self.Map, 'CS', np, self.T)
        requests1 = RG.requests
        requests2 = []
        offR = 0

        for i in range(np, self.reqN):
            sta0 = random.randrange(self.staN // 2) + (self.staN // 2) * (i % 2)
            sta1 = (sta0 + random.randrange(1, self.staN // 2)) % (self.staN // 2) + (self.staN // 2) * ((i + 1) % 2)
            # change index 1~m to 0~m-1 for easy access of dist[][]

            d = self.dists[sta0][sta1] * (1 + random.random())
            # make time interval random value between distance and 2*distance
            t0 = random.randrange(math.floor(self.runT - d))
            t1 = int(math.floor(t0 + d))

            td = t0 - tdis
            if td <= 0:
                tO = 0
            else:
                tO = random.randrange(0, td)
            requests2.append((t0, sta0, t1, sta1, tO))

        lst = requests1 + requests2
        return self.ensureOFF(lst)

    def ensureOFF(self, lst):
        offR = 0
        for r in lst:
            if r[4] == 0: offR += 1

        idx = 0  # ensure offline requests number = self.offRN
        # case : smaller number of offline
        while offR < self.offRN:
            if offR == self.offRN: break
            req = lst[idx]
            if req[4] != 0:
                lst[idx] = (req[0], req[1], req[2], req[3], 0)
                offR += 1
            idx += 1

        # case : larger number of offline
        while offR > self.offRN:
            if offR == self.offRN: break
            req = self.makeReq()
            while req[4] == 0:
                req = self.makeReq()

            jdx = 0
            while jdx < len(lst):
                if lst[jdx][4] == 0:
                    lst[jdx] = copy.deepcopy(req)
                    break
                jdx += 1
            offR -= 1

        return lst

    def similarTable(self):
        ret = []
        for requestidx in range(self.reqN):
            rw = []
            request = self.requests[requestidx]
            su = 0.0
            for request2 in self.requests:
                dreq = (request2[0] - request[0]) ** 2 +\
                       (request2[2] - request[2]) ** 2 +\
                       (self.Map.dists[request2[1]][request[1]]) ** 2 +\
                       (self.Map.dists[request2[3]][request[3]]) ** 2
                if dreq > 0: su += 1 / dreq

            for request2 in self.requests:
                dreq = (request2[0] - request[0]) ** 2 +\
                       (request2[2] - request[2]) ** 2 +\
                       (self.Map.dists[request2[1]][request[1]]) ** 2 +\
                       (self.Map.dists[request2[3]][request[3]]) ** 2
                if dreq > 0:
                    rw.append((1 / dreq) / su)
                else:
                    rw.append(0.0)
            ret.append(rw)
        return ret

    def rDS(self):
        sum = 0
        for r in self.requests:
            d = self.dists[r[1]][r[3]]
            dt = r[2] - r[0]
            sum += 1.0 * dt / d
        return sum / self.reqN