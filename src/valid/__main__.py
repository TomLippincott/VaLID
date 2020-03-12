import argparse
import logging
import gzip
import pickle
from .model import Classifier

def train(args):
    model = Classifier(args.n)
    with (gzip.open if args.data.endswith("gz") else open)(args.data, "rt") as ifd:
        for line in ifd:
            cid, label, text = line.strip().split("\t")
            model.train(label, text)
    with (gzip.open if args.output.endswith("gz") else open)(args.output, "wb") as ofd:
        pickle.dump(model, ofd)
            
def update(args):
    with (gzip.open if args.input.endswith("gz") else open)(args.input, "rb") as ifd:
        model = pickle.load(ifd)
    with (gzip.open if args.data.endswith("gz") else open)(args.data, "rt") as ifd:
        for line in ifd:
            cid, label, text = line.strip().split("\t")
            model.train(label, text)
    with (gzip.open if args.output.endswith("gz") else open)(args.output, "wb") as ofd:
        pickle.dump(model, ofd)        

def apply(args):
    with (gzip.open if args.input.endswith("gz") else open)(args.input, "rb") as ifd:
        model = pickle.load(ifd)
    total = 0
    correct = 0
    with (gzip.open if args.data.endswith("gz") else open)(args.data, "rt") as ifd:
        with (gzip.open if args.output.endswith("gz") else open)(args.output, "wt") as ofd:
            for line in ifd:
                cid, label, text = line.strip().split("\t")
                guess = model.classify(text)
                total += 1
                if label == guess:
                    correct += 1
                ofd.write("{}\t{}\t{}\t{}\n".format(cid, label, guess, text))
    print("Accuracy: {}".format(float(correct) / total))


            
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.set_defaults(mode=lambda x : None)
    subparsers = parser.add_subparsers()

    train_parser = subparsers.add_parser("train")
    train_parser.add_argument("-d", "--data", dest="data", required=True, help="Input data file")
    train_parser.add_argument("-o", "--output", dest="output", required=True, help="Output model file")
    train_parser.add_argument("-n", "--n", dest="n", type=int, default=3, help="Maximum n-gram length")
    train_parser.set_defaults(mode=train)

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("-d", "--data", dest="data", required=True, help="Input data file")
    update_parser.add_argument("-i", "--input", dest="input", required=True, help="Input model file")
    update_parser.add_argument("-o", "--output", dest="output", required=True, help="Output model file")
    update_parser.set_defaults(mode=update)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("-d", "--data", dest="data", required=True, help="Input data file")    
    apply_parser.add_argument("-i", "--input", dest="input", required=True, help="Input model file")
    apply_parser.add_argument("-o", "--output", dest="output", required=True, help="Output file")
    apply_parser.set_defaults(mode=apply)
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    resp = args.mode(args)
