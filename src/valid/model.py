from . import utils
import pickle
import math
import logging
import io

class Compressor:

    def __init__(self, language_code, order):
        """
        """
        self.language_code = language_code
        self.order = order
        #self.stage = []
        self.counts = {}
        self.tcounts = {}
        #self.history = []
        
    # def save(self, fname=None, pick=True):
    #     """
    #     """
    #     if fname is None:
    #         fname = self.name + '.mod'
    #     self.stage = []
    #     with open(fname, "wb") as ofd:
    #         if pick:
    #             pickle.dump(self, ofd)
    #         else:
    #             marshal.dump(self.name, ofd)
    #             marshal.dump(self.order, ofd)
    #             marshal.dump(self.stage, ofd)
    #             marshal.dump(self.counts, ofd)
    #             marshal.dump(self.tcounts, ofd)

    # def load(self, file_name=None):
    #     """
    #     """
    #     with open(file_name, "rb") as ifd:
    #         x = Compressor(0)
    #         x = pickle.load(ifd)
    #     return x

    def prune(self, limit=2000000):
        """
        Prune tables by halving-counts and removing any singletons.
        While total number of keys > limit, halve counts, and then remove zeros.
        """
        while len(self.counts) + len(self.tcounts) > limit:
            self.tcounts = utils.remove_zeros(utils.halve(self.tcounts))
            self.counts = utils.remove_zeros(utils.halve(self.counts))

    def merge(self, file_name):
        """
        Merge counts of other (i.e., really partial) model (supports building via map reduce)
        """
        with open(file_name, 'rb') as ifd:
            othermod = pickle.load(ifd)
        self.counts = utils.merge_maps(self.counts, othermod.counts)
        self.tcounts = utils.merge_maps(self.tcounts, othermod.tcounts)
       
    def train(self, file_name):
        """
        """
        with io.open(file_name, encoding="utf-8") as ifd:
            for document in ifd:
                self.add(document)

    def test(self, file_name):
        """
        Return log odds.
        """
        with io.open(file_name, encoding="utf-8") as ifd:
            return sum([self.score(line) for line in ifd])

    def add(self, document):
        """        
        """
        history = []
        for c in document:
            history.append(c)
            for j in range(0, self.order+1):
                if j < len(history):
                    x = history[len(history)-j:]
                    q = ''.join(x)
                    self.counts[q] = self.counts.get(q, 0) + 1
                    q = ''.join(x[0:len(x)-1])
                    self.tcounts[q] = self.tcounts.get(q, 0) + 1
            if len(history) > self.order:
                history = history[1:]

    def score(self, document):
        """
        Score a document based on the current state of the n-gram counts.
        """
        history = []
        score = 0
        for c in document:
            history.append(c)
            # look at contexts from longest to shortest
            didfind=False
            for j in range(self.order+1, -1, -1):
                x = history[len(history)-j:]
                q = ''.join(x)
                if q in self.counts:
                    cnt = self.counts[q]
                    q = ''.join(x[0:len(x)-1])
                    denom = self.tcounts[q]
                    score += math.log(float(cnt) / (1+denom))
                    didfind=True
                else:
                    # didn't ever see this char in *this context* before, else wouldn't make it here
                    q = ''.join(x[0:len(x)-1])
                    if q in self.tcounts:
                        denom = self.tcounts[q]
                        score += math.log(float(1) / (1+denom)) # emit escape prob
                    else:
                        score += math.log(float(1) / (1+1)) # emit escape prob (happens because not adapting while scoring)
            if not didfind:
                score += math.log(float(1) / 256) # who knowz what the coding alphabet size is...
            if len(history) > self.order:
                history = history[1:]
        return score


class LidClassifier(object):

    def __init__(self, code_lookup={}, preprocess=None):
        """
        """
        self.models = {}
        self.compressors = {}
        self.preprocess = preprocess
        self.code_lookup = code_lookup

    def add(self, compressor, language_code=None):
        """
        """
        #code = 
        self.compressors[language_code if language_code else compressor.language_code] = compressor
        #pass
        #with open(file_name, 'rb') as ifd:
        #    self.models[language_id] = pickle.load(ifd)
        
    def classify(self, document):
        """
        Given a tweet, return a map from language code to probability.
        """
        if self.preprocess:
            document = self.preprocess(document)
        tlen = len(document)
        scoresum = 0
        langscores = {}
        for l, c in self.compressors.iteritems():
            mscore = c.score(document)
            if tlen != 0:
                mscore = (mscore / tlen)
                scoresum += mscore
            langscores[l] = mscore
        print langscores
        return langscores
