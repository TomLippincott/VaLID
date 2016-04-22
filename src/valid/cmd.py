import argparse
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
            c.train(options.input)
            c.save(fname=options.output)
    elif options.action == "test":
        pass
    #for file_name in glob(os.path.join(options.input, "*")):
    #        c = model.Compressor(options.n)
    #        c.load(file_name)
    #        m.add(file_name, c)
        
