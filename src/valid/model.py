from . import utils
import pickle
import math
import logging
import io


class Compressor(object):

    def __init__(self, order, alphabet_size):
        """
        """
        self.order = order
        self.counts = {}
        self.tcounts = {}
        self.alphabet_size = alphabet_size
        
    def prune(self, limit=None):
        """
        Prune tables by halving-counts and removing any singletons.
        While total number of keys > limit, halve counts, and then remove zeros.
        """
        if limit:
            while len(self.counts) + len(self.tcounts) > limit:
                self.tcounts = utils.remove_zeros(utils.halve(self.tcounts))
                self.counts = utils.remove_zeros(utils.halve(self.counts))

    def merge(self, other):
       """
       Merge counts of other (i.e., really partial) model (supports building via map reduce)
       """
       self.counts = utils.merge_maps(self.counts, other.counts)
       self.tcounts = utils.merge_maps(self.tcounts, other.tcounts)
       
    def add(self, sequence):
        """        
        """

        history = []
        for c in sequence:
            history.append(c)
            for j in range(0, self.order+1):
                if j < len(history):
                    x = history[len(history)-j:]
                    q = tuple(x)
                    self.counts[q] = self.counts.get(q, 0) + 1
                    q = tuple(x[0:len(x)-1])
                    self.tcounts[q] = self.tcounts.get(q, 0) + 1
            if len(history) > self.order:
                history = history[1:]

    def apply(self, sequence):
        """
        Score a sequence based on the current state of the n-gram counts.
        """
        history = []
        score = 0
        for c in sequence:
            history.append(c)
            # look at contexts from longest to shortest
            didfind=False
            for j in range(self.order+1, -1, -1):
                x = history[len(history)-j:]
                q = tuple(x)
                #q = ''.join(x)
                if q in self.counts:
                    cnt = self.counts[q]
                    #q = ''.join(x[0:len(x)-1])
                    q = tuple(x[0:len(x)-1])
                    denom = self.tcounts[q]
                    score += math.log(float(cnt) / (1+denom))
                    didfind=True
                else:
                    # didn't ever see this char in *this context* before, else wouldn't make it here
                    q = tuple(x[0:len(x)-1])
                    if q in self.tcounts:
                        denom = self.tcounts[q]
                        score += math.log(float(1) / (1+denom)) # emit escape prob
                    else:
                        score += math.log(float(1) / (1+1)) # emit escape prob (happens because not adapting while scoring)
            if not didfind:
                score += math.log(1.0 / self.alphabet_size) # who knowz what the coding alphabet size is...
            if len(history) > self.order:
                history = history[1:]
        return score


class Classifier(object):

    def __init__(self, order=3, alphabet_size=256):
        """
        """
        self.order = order
        self.compressors = {}
        self.alphabet_size = alphabet_size
                
    def train(self, label, sequence):
        self.compressors[label] = self.compressors.get(label, Compressor(self.order, self.alphabet_size))
        self.compressors[label].add(sequence)
        
    def predict(self, sequence):
        """
        Given a sequence, return a map from label to log-probability.
        """
        tlen = len(sequence)
        scoresum = 0
        scores = {}
        for l, c in self.compressors.items():
            mscore = c.apply(sequence)
            #if tlen != 0:
            #    mscore = (mscore / tlen)
            #    scoresum += mscore
            scores[l] = mscore
        return scores
    
    def classify(self, sequence):
        probs = self.predict(sequence)
        best = sorted(probs.items(), key=lambda x : x[1], reverse=True)[0][0]
        return best

    def merge(self, other):
        for l, c in other.compressors.items():
            if l not in self.compressors:
                self.compressors[l] = c
            else:
                self.compressors[l].merge(c)
