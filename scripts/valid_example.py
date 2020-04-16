import argparse
import sys
import random
from valid.model import Classifier
import re
import pickle
import gzip
import logging
from sklearn.metrics import f1_score

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Example of running VaLID over stdin lines formatted as 'LABEL<TAB>TEXT' or 'ID<TAB>LABEL<TAB>TEXT'")
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
        elif len(toks) == 3:
            _, label, text = toks
        else:
            continue
        seq = []
        for v in re.split(r"\s+", text) if args.type == "words" else text if args.type == "characters" else text.encode():
            seq.append(v)
        instances.append((seq, label))
        label_counts[label] = label_counts.get(label, 0) + 1
    
    logging.info("Shuffling data and creating train/dev/test split...")
    random.shuffle(instances)
    train = [i for i in instances[:int(.8 * len(instances))]]
    dev = [i for i in instances[int(.8 * len(instances)):int(.9 * len(instances))]]
    test = [i for i in instances[int(.9 * len(instances)):]]
    train_alphabet = set()
    for s, l in train:
        for v in s:
            train_alphabet.add(v)
            
    best_model, best_score, best_n = None, 0.0, 0
    for n in range(1, 4):
        logging.info("Training %d-gram model on train set...", n)
        model = Classifier(order=n, alphabet_size=len(train_alphabet))
        model.fit([s for s, _ in train], [l for _, l in train])
        logging.info("Applying %d-gram model to dev set...", n)
        correct = 0
        guesses = model.predict([s for s, _ in dev])
        labels = [l for _, l in dev]
        
        score = f1_score(labels, guesses, average="macro")
        logging.info("%d-gram dev score: %f", n, score)
        if score > best_score or best_model == None:
            best_score = score
            best_model = model
            best_n = n
    
    logging.info("Applying best model (%d-gram) to test set...", best_n)

    guesses = model.predict([s for s, l in test])
    labels = [l for _, l in test]
    score = f1_score(labels, guesses, average="macro")
    logging.info("%d-gram test score: %.3f", best_n, score)
    
    if args.output:
        logging.info("Saving best model (%d-gram) to %s", best_n, args.output)
        with gzip.open(args.output, "wb") as ofd:
            pickle.dump(best_model, ofd)
