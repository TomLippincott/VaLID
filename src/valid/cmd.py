import argparse
import pickle
from glob import glob
from . import model, languages, utils    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-m", "--model", dest="model")
    parser.add_argument("-n", "--n", dest="n", help="Maximum ngram-character-history length", type=int, default=5)
    parser.add_argument("-a", "--action", dest="action", choices=["train", "test"])
    parser.add_argument(dest="inputs", nargs="+", help="Either a list of files to classify, or alternating between language ID and training file")
    options = parser.parse_args()

    m = model.LidClassifier()
    if options.action == "train":
        for i in range(len(options.inputs) / 2):
            c = model.Compressor(options.n)
            c.train(options.inputs[i * 2])
            m.add(c, options.inputs[(i * 2) + 1])
        with open(options.output, "w") as ofd:
            pickle.dump(m, ofd)
    elif options.action == "test":
        pass
        
