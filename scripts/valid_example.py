import argparse
import sys
import random
from valid.model import Classifier
import re
import pickle
import gzip
import logging


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Example of running VaLID over stdin lines formatted as 'LABEL<TAB>TEXT")
    parser.add_argument("--type", dest="type", default="characters", choices=["words", "characters", "bytes"],
                        help="Encode whitespace-delimited words, UTF characters, or bytes")
    parser.add_argument("--output", dest="output", help="File to serialize best model to")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    logging.info("Reading data from stdin...")
    label_counts = {}
    instances = []
    for line in sys.stdin:
        toks = line.strip().split("\t")
        if len(toks) == 2:
            label, text = toks
            seq = []
            for v in re.split(r"\s+", text) if args.type == "words" else text if args.type == "characters" else text.encode():
                seq.append(v)
            instances.append({"label" : label, "sequence" : seq})
            label_counts[label] = label_counts.get(label, 0) + 1

    logging.info("Shuffling data and creating train/dev/test split...")
    random.shuffle(instances)
    train = [i for i in instances[:int(.8 * len(instances))]]
    dev = [i for i in instances[int(.8 * len(instances)):int(.9 * len(instances))]]
    test = [i for i in instances[int(.9 * len(instances)):]]
    train_alphabet = set()
    for i in train:
        for v in i["sequence"]:
            train_alphabet.add(v)
            
    best_model, best_score, best_n = None, 0.0, 0
    for n in range(1, 6):
        logging.info("Training %d-gram model on train set...", n)
        model = Classifier(order=n, alphabet_size=len(train_alphabet))
        for i in train:
            model.train(i["label"], i["sequence"])
        logging.info("Applying %d-gram model to dev set...", n)
        correct = 0
        for i in dev:
            guess = model.classify(i["sequence"])
            if guess == i["label"]:
                correct += 1
        acc = correct / len(dev)
        logging.info("%d-gram dev accuracy: %f", n, acc)
        if acc > best_score or best_model == None:
            best_score = acc
            best_model = model
            best_n = n
    
    logging.info("Applying best model (%d-gram) to test set...", best_n)
    correct = 0.0
    for i in test:
        guess = best_model.classify(i["sequence"])
        if guess == i["label"]:
            correct += 1
    acc = correct / len(test)
    logging.info("%d-gram test accuracy: %.3f", best_n, acc)
    
    if args.output:
        logging.info("Saving best model (%d-gram) to %s", best_n, args.output)
        with gzip.open(args.output, "wb") as ofd:
            pickle.dump(best_model, ofd)
