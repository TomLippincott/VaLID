
if __name__ == "__main__":

    import gzip
    import re
    import argparse
    import pickle
    from valid.model import Classifier, Compressor

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument(dest="inputs", nargs="+", help="A list alternating between label and model file (in old \"invalid\" format)")
    options = parser.parse_args()

    model = None
    
    for i in range(len(options.inputs) / 2):
        label = options.inputs[i * 2]
        fname = options.inputs[i * 2 + 1]
        print(label, fname)
        with open(fname) as ifd:
            text = re.sub(r"^\(ippm\nCompressor", "(ivalid.model\nCompressor", ifd.read())
            compressor = pickle.loads(text)
            compressor.counts = {tuple(k) : v for k, v in compressor.counts.iteritems()}
            compressor.tcounts = {tuple(k) : v for k, v in compressor.tcounts.iteritems()}
            compressor.alphabet_size = 256
            if model == None:
                model = Classifier(compressor.order)
            model.compressors[label] = compressor
        
    with gzip.open(options.output, "w") as ofd:
        pickle.dump(model, ofd)
