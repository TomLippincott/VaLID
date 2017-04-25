from . import languages
import re
import io
import logging

def normalizeTweet(s):
    tw = re.sub(r"\s+", " ", s.lower())
    tw = re.sub(r"(@|https?://)[^\s]+", "", tw)
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
