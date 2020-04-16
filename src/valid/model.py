from . import utils
import pickle
import math
import logging
import io
from collections import deque
import numpy


class Classifier(object):

    def __init__(self, order=3, alphabet_size=256):
        """
        """
        self.order = order
        self.alphabet_size = alphabet_size
        self.counts = {}
        self.tcounts = {}
        self.labels = set()

    def fit(self, X, y):
        for t, l in zip(X, y):
            self.train(l, t)

    def predict(self, X):
        return [self.classify(x) for x in X]

    def predict_log_proba(self, X):
        pass    
    
    def train(self, label, sequence):
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
            if len(history) > self.order:
                history = history[1:]


        
        
    def probabilities(self, sequence):
        """
        Given a sequence, return a map from label to log-probability.
        """
        history = ()
        scores = {k : 0.0 for k in self.labels}
        for c in sequence:
            history += (c,)

            # look at contexts from longest to shortest
            found = {label : False for label in self.labels}

            for j in range(self.order+1, -1, -1):
                q = history[len(history)-j:]
                r = q[0:len(q)-1]                
                for label in self.labels:
                    numer = self.counts.get(q, {}).get(label, 0)
                    denom = self.tcounts.get(r, {}).get(label, 0)                    
                    if numer != 0:
                        found[label] = True
                    numer = max(numer, 1)
                    denom = max(denom, 1)
                    val = math.log(float(numer) / (1+denom))
                    scores[label] += val
                for label in self.labels:
                    if not found[label]:
                        scores[label] += math.log(1.0 / self.alphabet_size)
            if len(history) > self.order:
                history = history[1:]
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
