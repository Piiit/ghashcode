# -*- coding: utf-8 -*-

files = ["kittens.in", "me_at_the_zoo.in", "trending_today.in", "videos_worth_spreading.in"]

import collections
Video = collections.namedtuple('Video', 'id, size, requests')
Request = collections.namedtuple('Request', 'id, count, video, endPointId')
EndPoint = collections.namedtuple('EndPoint', 'id, latencyDC, noCaches, connections')
Connection = collections.namedtuple('Connection', 'cacheId, latencyC')

class Cache:
    def __init__(self, id, capacity):
        self.id = int(id)
        self.capacity = int(capacity)
        self.videos = []

    def __str__(self):
        return 'Cache(id=%d, capacity=%d)' % (self.id, self.capacity)

class Farm:
    def __init__(self, fn):
        file = open(fn, "r")

        #Videos, Endpoints, Requests, Caches, Capacities(X)
        (self.V, self.E, self.R, self.C, self.X) = [int(x) for x in file.readline().split(" ")]

        # Generate Caches
        self.caches = []
        for c in range(self.C):
            self.caches.append(Cache(c, self.X))

        # Generate all videos
        maxVS = 0
        minVS = 0
        avgVS = 0
        self.videos = []
        i = 0
        for x in file.readline().split(" "):
            x = int(x)
            self.videos.append(Video(i, x, []))

            maxVS = max(maxVS, x)
            minVS = min(minVS, x)
            avgVS += x
            i += 1

        avgVS /= len(self.videos)

        # Generate all endpoints
        maxConn = 0
        minConn = 0
        avgConn = 0
        self.endPoints = []
        i = 0
        while True:
            ret = file.readline().split(" ")

            # Break if all endpoints read in...
            if ret == None or len(ret) == 3:
                break

            (latencyDC, noCaches) = [int(x) for x in ret]

            connections = []
            for cache in range(noCaches):
                (cacheId, latencyC) = [int(x) for x in file.readline().split(" ")]
                connections.append(Connection(cacheId, latencyC))


            self.endPoints.append(EndPoint(i, latencyDC, noCaches, connections))

            maxConn = max(noCaches, maxConn)
            minConn = min(noCaches, minConn)
            avgConn += noCaches

            #print(self.endPoints[i])
            i += 1


        # Requests
        request = Request(0, int(ret[2]), int(ret[0]), int(ret[1]))
        self.requests = []
        self.requests.append(request)
        self.videos[request.video].requests.append(request)

        i = 1
        while True:
           ret = file.readline().split(" ")
           if ret == None or len(ret) != 3:
               break

           (video, endpoint, noOfReq) = [int(x) for x in ret]
           request = Request(i, noOfReq, video, endpoint)
           self.requests.append(request)
           self.videos[video].requests.append(request)
           i += 1

        print()
        print("-------------------------------------")
        print("FILE =", fn)
        print("Videos              : ", self.V)
        print("Endpoints           : ", self.E)
        print("Requests            : ", self.R)
        print("Caches              : ", self.C)
        print("Capacity            : ", self.X)
        print("Endpoint->Cache: min: ", minConn)
        print("Endpoint->Cache: max: ", maxConn)
        print("Endpoint->Cache: avg: ", avgConn / len(self.endPoints))
        print("Video Size     : min: ", minVS)
        print("Video Size     : max: ", maxVS)
        print("Video Size     : avg: ", avgVS)


    def calcScore2(self, video, cache):
        """
        Calculations without numpy arrays, just lists... this is much faster!
        """
        s = 0
        for i, re in enumerate(video.requests):
            ep = self.endPoints[re.endPointId]
            try:
                latencyEPC = ep.connections[cache.id].latencyC
            except:
                latencyEPC = 0

            latencyEPDC = ep.latencyDC
            s += re.count * (latencyEPDC - latencyEPC)

        return s


    def calcAll(self):
        self.all = []
        for i, v in enumerate(self.videos):
            if i % 100 == 0:
                print("...for video", v.id)
            for c in self.caches:
                self.all.append((self.calcScore2(v,c), v.id, c.id))

        self.all = sorted(self.all, key=lambda x: x[0], reverse=True)


        for x in self.all:
            cache = self.caches[x[2]]
            video = self.videos[x[1]]

            if cache.capacity - video.size >= 0:

                if x[1] in cache.videos:
                    print("ERROR")

                cache.videos.append(x[1])
                cache.capacity -= video.size


import sys

print("Reading file...")
inputfile = sys.argv[1]
farm = Farm(inputfile)


#print("Calcolating new structures...")
#farm.newStructs()

#print(farm.cacheEndP)

#farm.calcolateScore(0, 0)
print("Calcolating scores of %d videos..." % len(farm.videos))
farm.calcAll()

import datetime

now = datetime.datetime.now()


print("Writing result to file")
with open("result-%s-%s.txt" % (now.isoformat(), inputfile), "a") as resultfile:
    resultfile.write("%d\n" % len(farm.caches))
    for x in farm.caches:
        resultfile.write("%d " % x.id)
        for v in x.videos:
            resultfile.write("%d " % v)
        resultfile.write("\n")

print("DONE")



