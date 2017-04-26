import argparse
import pickle
import gzip
from glob import glob
from model import Classifier    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-m", "--model", dest="model")
    parser.add_argument("-n", "--n", dest="n", help="Maximum ngram-character-history length", type=int, default=5)
    parser.add_argument(dest="inputs", nargs="+", help="A list alternating between label and text file with one document per line")
    options = parser.parse_args()


    if options.model:
        # apply        
        with gzip.open(options.model) as ifd:
            model = pickle.load(ifd)
        print(model.compressors.keys())
        total = 0
        correct = 0
        for i in range(len(options.inputs) / 2):
            label = options.inputs[i * 2]
            fname = options.inputs[(i * 2) + 1]
            with open(fname) as ifd:
                for line in ifd:
                    probs = model.classify(line)
                    guess = max(probs.iteritems(), key=lambda x : x[1])[0]
                    total += 1
                    if label == guess:
                        correct += 1
        print("Accuracy: {}".format(float(correct) / total))
    else:
        # train
        model = Classifier(options.n)
        for i in range(len(options.inputs) / 2):
            label = options.inputs[i * 2]
            fname = options.inputs[(i * 2) + 1]
            with open(fname) as ifd:
                for line in ifd:
                    model.train(label, line)
        with gzip.open(options.output, "w") as ofd:
            pickle.dump(model, ofd)
        
