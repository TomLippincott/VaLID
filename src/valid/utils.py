from . import languages
#from . import model
import re
import io
import logging

def normalizeTweet(s):
    tw = re.sub(r"\s+", " ", s.lower())
    tw = re.sub(r"(@|https?//)[^\s]+", "", tw)
    return tw.strip()

def remove_zeros(m):
    """
    Remove keys from map with value = 0.
    """
    return {k : v for k, v in m.iteritems() if v > 0}

def halve(m):
    """
    Divide each integer value in map by two.
    """
    return {k : v // 2 for k, v in m.iteritems()}

def merge_maps(map_A, map_B, combinator=lambda x, y : x + y):
    """
    Combine two maps using a combinator function to handle collisions.
    """
    for k, v in map_B.iteritems():
        map_A[k] = combinator(v, map_A[k]) if k in map_A else v
    return map_A


# def slurp(fname, encoding='utf-8'):
#     with io.open(fname, 'r', encoding=encoding, newline='\n') as ifd:
#         return [l for l in ifd]

# def getModel(filename, order, prefix, lang, maxsize=0):
#     m = model.Compressor(order, name='%s' % lang)
#     modelfile = os.path.join(prefix, m.name + '.' + str(m.order) + '.mod')
#     if os.path.exists(modelfile):
#         m = m.load(fname=modelfile, pick=True) # False
#     else:
#         if os.path.exists(filename):
#             m.train('%s' % filename)
#             if maxsize > 0:
#                 m.prune(limit=maxsize)
#             m.save(fname=modelfile, pick=True) # False
#         else:
#             print >>sys.stderr, ('Warning: unable to load model %s '
#                                  '(looked in %r)' % (m.name, modelfile))
#             return None
#         #print "Trained model: %s" % model.name
#         #sys.stdout.flush()
#     return m
