import collections
import ipc
import numpy
from numpy import abs
import h5py
import time, datetime

class Stack:
    def __init__(self,name="stack",maxLen=100,rank=0):
        self._rank = rank
        self._maxLen = maxLen
        self._name = name
        self.clear()
    def clear(self):
        self._buffer = None
        self._currentIndex = 0
    def filled(self):
        return self._currentIndex > self._maxLen
    def add(self,data):
        if self._buffer is None:
            s = tuple([self._maxLen] + list(data.shape))
            self._buffer = numpy.zeros(shape=s, dtype=data.dtype)
        self._buffer[self._currentIndex % self._maxLen,:] = data[:]
        self._currentIndex += 1
        print data.shape
    def _getData(self):
        if self.filled():
            return self._buffer
        else:
            return self._buffer[:self._currentIndex]
    def std(self):
        return self._getData().std(axis=0)
    def mean(self):
        return self._getData().mean(axis=0)
    def sum(self):
        return self._getData().sum(axis=0)
    def median(self):
        return numpy.median(self._getData(),axis=0)
    def write(self,evt,directory=".",outputs=None,png=False,interval=None):
        if interval is not None:
            if (self._currentIndex % interval) != 0:
                return
        if outputs is None:
            outputs = ["std","mean","sum","median"]
        fn = "%s/%s-%i-%i.h5" % (directory,self._name, evt.event_id(), self._rank)
        with h5py.File(fn,"w") as f:
            for o in outputs:
                exec "%s = self.%s()" % (o,o)
                exec "f[\"%s\"] = %o" % (o,o)
        if png:
            import matplotlib.pyplot as pypl
            for o in outputs:
                fn = "%s/%s-%s-%i-%i.png" % (directory,o,self._name, evt.event_id(), self._rank) 
                exec "pypl.imsave(fn,%s)" % o

