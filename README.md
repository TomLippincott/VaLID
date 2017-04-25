# VaLID: compression-based text classification

This library implements Prediction by Partial Matching (PPM),
originally for language identification (LID), but suitable
for arbitrary tasks assigning discrete labels to sequences.
Output scores are log prob values representing the likelihood 
of a model on an average character basis. 

## Quick start

Training a classification model is very simple.  Assuming you 
have sequences of hashable values (e.g. characters) associated
with labels:

```python
from valid.model import Classifier

c = Classifier(order=4)
for text in englishtexts:
	c.train("eng", text)
for text in spanish_texts:
	c.train("spa", text)	
```

You can then apply the model to new data points:

```python
>>> print c.classify("Some English text")
{"eng" : -0.1, "spa" : -0.00002}
```

Note that it returns log-probabilities for each possible label. 
The model can be serialized with the pickle library:

```python
import gzip
import pickle
with gzip.open(model_file, "w") as ofd:
	pickle.dump(c, ofd)
```

Later, it can be deserialized to be applied to test data, or
trained further:

```python
import gzip
import pickle
with gzip.open(model_file) as ifd:
	c = pickle.load(ifd)
```

## LID and Tweet functionality

The `normalizeTweet` function in `valid.utils` may be useful 
for preprocessing microblog texts before training.

There are three lookup tables in `valid.languages`:

1. `ALL_LANGUAGES` is a list of iso639-1 language codes
2. `MAJOR_LANGUAGES` is a subset of major languages
3. `MAP_2_TO_3` is a best-effort map from iso639-1 to iso639-3

## Further reading

If you use this code in published work please cite the following paper:

http://aclweb.org/anthology-new/W/W12/W12-2108.pdf

Short bibliography of compression language models used in NLP:

Bendetto et al., 'Language Trees and Zipping'
(used for author ID and language ID)
 http://www.ccs.neu.edu/home/jaa/CSG195.08F/Topics/Papers/BenedettoCaLo.pdf

Pavelec et al, 'Author Identification Using Compression Models':
 http://www.cvc.uab.es/icdar2009/papers/3725a936.pdf

Bratko et al, 'Spam Filtering Using Statistical Data Compression Models':
 http://jmlr.csail.mit.edu/papers/volume7/bratko06a/bratko06a.pdf

A talk by Gord Cormack:
 http://plg.uwaterloo.ca/~gvcormac/cormack-nato.pdf

Frank et al., 'Text categorization using compression models'
 http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.148.9031

Teahan, 'Text classification and segmentation using minimum cross-entropy'
 http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.25.8114

Marton et al, 'On compression based text classification'
 http://www.umiacs.umd.edu/~ymarton/pub/ecir05/final.pdf

 
Papers about the Prediction by Partial Matching (PPM) algorithm:

Cleary and Witten, "Data Compression Using Adaptive Coding and Partial String Matching", IEEE Trans on Comms, 32(4), 1984.

Alistair Moffat, 'Implementing the PPM Data Compression Scheme', IEEE
Trans. on Comms, 38(11), 1990.
