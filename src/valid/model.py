from . import utils
import pickle
import math
import logging
import io
from collections import deque
import numpy

# class Compressor(object):

#     def __init__(self, order, alphabet_size):
#         """
#         """
#         self.order = order
#         self.counts = {}
#         self.tcounts = {}
#         self.alphabet_size = alphabet_size
        
#     def prune(self, limit=None):
#         """
#         Prune tables by halving-counts and removing any singletons.
#         While total number of keys > limit, halve counts, and then remove zeros.
#         """
#         if limit:
#             while len(self.counts) + len(self.tcounts) > limit:
#                 self.tcounts = utils.remove_zeros(utils.halve(self.tcounts))
#                 self.counts = utils.remove_zeros(utils.halve(self.counts))

#     def merge(self, other):
#        """
#        Merge counts of other (i.e., really partial) model (supports building via map reduce)
#        """
#        self.counts = utils.merge_maps(self.counts, other.counts)
#        self.tcounts = utils.merge_maps(self.tcounts, other.tcounts)
       
#     def add(self, sequence):
#         """        
#         """

#         history = []
#         for c in sequence:
#             history.append(c)
#             for j in range(0, self.order+1):
#                 if j < len(history):
#                     x = history[len(history)-j:]
#                     q = tuple(x)
#                     self.counts[q] = self.counts.get(q, 0) + 1
#                     q = tuple(x[0:len(x)-1])
#                     self.tcounts[q] = self.tcounts.get(q, 0) + 1
#             if len(history) > self.order:
#                 history = history[1:]

#     def apply(self, sequence):
#         """
#         Score a sequence based on the current state of the n-gram counts.
#         """
#         history = ()
#         score = 0
#         for c in sequence:
#             history += (c,)
#             # look at contexts from longest to shortest
#             didfind=False

#             for j in range(self.order+1, -1, -1):
#                 q = history[len(history)-j:]
#                 if q in self.counts:
#                     cnt = self.counts[q]
#                     q = q[0:len(q)-1]
#                     denom = self.tcounts[q]
#                     score += math.log(cnt / (1+denom))
#                     didfind=True
#                 else:
#                     # didn't ever see this char in *this context* before, else wouldn't make it here
#                     q = q[0:len(q)-1]
#                     if q in self.tcounts:
#                         denom = self.tcounts[q]
#                         score += math.log(float(1) / (1+denom)) # emit escape prob
#                     else:
#                         score += math.log(float(1) / (1+1)) # emit escape prob (happens because not adapting while scoring)
#             if not didfind:
#                 score += math.log(1.0 / self.alphabet_size) # who knowz what the coding alphabet size is...
#             if len(history) > self.order:
#                 history = history[1:]
#         return score


class Classifier(object):

    def __init__(self, order=3, alphabet_size=256):
        """
        """
        self.order = order
        self.alphabet_size = alphabet_size
        #self.compressors = {}
        self.counts = {}
        self.tcounts = {}
        self.labels = set()
        #self.cache = {}

    def fit(self, X, y):
        pass

    def predict(self, X):
        pass

    def predict_log_proba(self, X):
        pass    
    
    def train(self, label, sequence):
        #self.compressors[label] = self.compressors.get(label, Compressor(self.order, self.alphabet_size))
        #self.compressors[label].add(sequence)
        self.labels.add(label)
        history = []
        for c in sequence:
            history.append(c)
            for j in range(0, self.order+1):
                if j < len(history):
                    x = history[len(history)-j:]
                    q = tuple(x)
                    self.counts[q] = self.counts.get(q, {})
                    self.counts[q][label] = self.counts[q].get(label, 0) + 1
                    q = tuple(x[0:len(x)-1])
                    self.tcounts[q] = self.tcounts.get(q, {})
                    self.tcounts[q][label] = self.tcounts[q].get(label, 0) + 1
                    #self.tcounts[q] = self.tcounts.get(q, 0) + 1
            if len(history) > self.order:
                history = history[1:]


        
        
    def probabilities(self, sequence):
        """
        Given a sequence, return a map from label to log-probability.
        """
        #tlen = len(sequence)
        #scoresum = 0
        #scores = {}
        history = ()
        scores = {k : 0.0 for k in self.labels}
        for c in sequence:
            history += (c,)

            # look at contexts from longest to shortest
            found = {label : False for label in self.labels}

            for j in range(self.order+1, -1, -1):
                q = history[len(history)-j:]
                #if q in self.cache:
                #    for label in self.labels:
                #        scores[label] += self.cache[q][label]
                #else:
                #    self.cache[q] = {}
                r = q[0:len(q)-1]                
                for label in self.labels:
                    #, count in self.counts.get(q, {}).items():
                    numer = self.counts.get(q, {}).get(label, 0)
                    denom = self.tcounts.get(r, {}).get(label, 0)                    
                    if numer != 0:
                        found[label] = True
                    numer = max(numer, 1)
                    denom = max(denom, 1)

                    # if q in self.counts:
                    #     cnt = self.counts[q]

                    #denom = self.tcounts[label][r]
                    val = math.log(float(numer) / (1+denom))
                    #self.cache[q][label] = val
                    scores[label] += val
                        #     didfind=True
                    #else:
                    #    # didn't ever see this char in *this context* before, else wouldn't make it here
                    #    q = q[0:len(q)-1]
                    #    if q in self.tcounts:
                    #         denom = self.tcounts[q]
                    #         score += math.log(float(1) / (1+denom)) # emit escape prob
                    #     else:
                    #         score += math.log(float(1) / (1+1)) # emit escape prob (happens because not adapting while scoring)
                for label in self.labels:
                    if not found[label]:
                        scores[label] += math.log(1.0 / self.alphabet_size)
            #if not didfind:
            #    score += math.log(1.0 / self.alphabet_size) # who knowz what the coding alphabet size is...
            if len(history) > self.order:
                history = history[1:]


        #for l, c in self.compressors.items():
        #    mscore = c.apply(sequence)
            #if tlen != 0:
            #    mscore = (mscore / tlen)
            #    scoresum += mscore
        #    scores[l] = mscore
        return scores
    
    def classify(self, sequence):
        probs = self.probabilities(sequence)
        best = sorted(probs.items(), key=lambda x : x[1], reverse=True)[0][0]
        return best

    def merge(self, other):
        for l, c in other.compressors.items():
            if l not in self.compressors:
                self.compressors[l] = c
            else:
                self.compressors[l].merge(c)
