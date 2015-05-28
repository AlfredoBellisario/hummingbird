import ipc
from backend import Record
import numpy as np
import collections

counter = collections.deque([])
def countHits(evt, hit, history=100):
    """Takes a boolean (True for hit, False for miss) and adds accumulated nr. of hits to ``evt["analysis"]["nrHit"]`` and 
    accumulated nr. of misses to ``evt["analysis"]["nrMiss"]``

    :Authors:
        Benedikt J. Daurer (benedikt@xray.bmc.uu.se),
        Jonas Sellberg 
    """
    global counter
    if counter.maxlen is None or (counter.maxlen is not history):
        counter = collections.deque([], history)
    if hit: counter.append(True)
    else: counter.append(False)
    evt["analysis"]["nrHit"]  = Record("nrHit",  counter.count(True))
    evt["analysis"]["nrMiss"] = Record("nrMiss", counter.count(False))

def hitrate(evt, hit, history=100):
    """Takes a boolean (True for hit, False for miss) and adds the hit rate in % to ``evt["analysis"]["hitrate"]`` if called by main worker, otherwise it returns None. Has been tested in MPI mode

    :Authors:
        Benedikt J. Daurer (benedikt@xray.bmc.uu.se)
    """
    countHits(evt, hit, history/ipc.mpi.nr_workers())
    hits = evt["analysis"]["nrHit"].data
    misses = evt["analysis"]["nrMiss"].data
    hitrate = np.array(100 * hits / float(hits + misses))
    ipc.mpi.sum(hitrate)
    if(ipc.mpi.is_main_worker()):
        evt["analysis"]["hitrate"] = Record("hitrate", hitrate[()]/ipc.mpi.nr_workers(), unit='%')
    else:
        evt["analysis"]["hitrate"] = None

def countLitPixels(evt, type, key, aduThreshold=20, hitscoreThreshold=200):
    """A simple hitfinder that counts the number of lit pixels and
    adds a boolean to ``evt["analysis"]["isHit" + key]`` and  the hitscore to ``evt["analysis"]["hitscore - " + key]``.

    Args:
        :evt:       The event variable
        :type(str): The event type (e.g. photonPixelDetectors)
        :key(str):  The event key (e.g. CCD)
    Kwargs:
        :aduThreshold(int):      only pixels above this threshold (in ADUs) are valid, default=20
        :hitscoreThreshold(int): events with hitscore (Nr. of lit pixels)  above this threshold are hits, default=200

    :Authors:
        Benedikt J. Daurer (benedikt@xray.bmc.uu.se)
    """
    detector = evt[type][key]
    hitscore = (detector.data > aduThreshold).sum()
    evt["analysis"]["isHit - " + key] = hitscore > hitscoreThreshold
    evt["analysis"]["hitscore - " + key] = Record("hitscore - " + key, hitscore)
