"""
From Coobook recipe:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/499335

Title: recursively update a dictionary without hitting "Python recursion limit"
Submitter: Robin Bryce (other recipes)
Last Updated: 2006/12/21
Version no: 1.2
Category:

Description:

This function recursively walks the items and values of two dict like objects.
At each level when a key exists in both, and each value is a dict,
then the destination dict is updated from the source dict usiing the builtin
dict.update method. After the operation all keys and values from the source,
at any level, will be referenced in the destination.
"""

from __future__ import print_function

class InputDataException(Exception):
    pass


def recursiveupdate(dst, src, one_sided=False):
    """Recursively update dst from src.

    Recursion depth is bounded by the heap rather than the python
    interpretor recursion limit.

    >>> dst = dict(a=1,b=2,c=dict(ca=31, cc=33, cd=dict(cca=1)), d=4, f=6)
    >>> src = dict(b='u2',c=dict(cb='u32', cd=dict(cda=dict(cdaa='u3411',
    ... cdab='u3412'))), e='u5')
    >>> r = recursiveupdate(dst, src)
    >>> assert r is dst
    >>> assert r['a'] == 1 and r['d'] == 4 and r['f'] == 6
    >>> assert r['b'] == 'u2' and r['e'] == 'u5'
    >>> assert dst['c'] is r['c']
    >>> assert dst['c']['cd'] is r['c']['cd']
    >>> assert r['c']['cd']['cda']['cdaa'] == 'u3411'
    >>> assert r['c']['cd']['cda']['cdab'] == 'u3412'
    >>> from pprint import pprint; pprint(r)
    {'a': 1,
     'b': 'u2',
     'c': {'ca': 31,
           'cb': 'u32',
           'cc': 33,
           'cd': {'cca': 1, 'cda': {'cdab': 'u3412', 'cdaa': 'u3411'}}},
     'd': 4,
     'e': 'u5',
     'f': 6}
    """
    #irecursiveupdate(dst, src.iteritems())
    #return dst
    return merge_dictionary(dst, src, one_sided)

def irecursiveupdate(dict_, biter):
    """Recursively update dict `dict_` from `biter`

    `biter` is assumed to be an iterable of the form::
        [(k0, v0), (k1, v1), ..., (kN, vN)]

        ie, the result of src.iteritems()
    `dict_` is assumed to be a dict or dict like instance.

    In the following `dst` is the intial value of `dict_` and `src` is
    the initial value of `biter`.

    For every key in src:
        If that key is also in dst and
        both dst[k] and src[k] are dicts then:
            recursiveupdate(dst[k], (src[k]))
        otherwise:
            dst[k] = src[k]

    """
    try:
        stack = []
        while biter:
            for (b_k, b_v) in biter:
                if (b_k in dict_
                    and isinstance(b_v, dict)
                    and isinstance(dict_[b_k], dict)):
                    stack.append((biter, dict_)) # current -> parent
                    break
                else:
                    dict_[b_k] = b_v
            else:
                while not biter:
                    biter, dict_ = stack.pop() # current <- parent
                continue
            biter, dict_ = b_v.iteritems(), dict_[b_k]
    except IndexError:
        pass

def merge_dictionary(dst, src, one_sided=False):
    """
    >>> dst = dict(a=1,b=2,c=dict(ca=31, cc=33, cd=dict(cca=1)), d=4, f=6, g=7)
    >>> src = dict(b='u2',c=dict(cb='u32', cd=dict(cda=dict(cdaa='u3411',
    ... cdab='u3412'))), e='u5', h=dict(i='u4321'))
    >>> r = merge_dictionary(dst, src)
    >>> assert r is dst
    >>> assert r['a'] == 1 and r['d'] == 4 and r['f'] == 6
    >>> assert r['b'] == 'u2' and r['e'] == 'u5'
    >>> assert dst['c'] is r['c']
    >>> assert dst['c']['cd'] is r['c']['cd']
    >>> assert r['c']['cd']['cda']['cdaa'] == 'u3411'
    >>> assert r['c']['cd']['cda']['cdab'] == 'u3412'
    >>> assert r['g'] == 7
    >>> assert src['h'] is r['h']
    """

    stack = [(dst, src)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                if one_sided and key not in ['value', 'meta_data', 'unit']:
                    msg = """
                    An error occurred while reading input data.
                    The keyword "%s" was specified but is not in allowed.
                    Only keywords from template files can be used.
                    """ % key
                    print(current_dst.keys())
                    raise InputDataException(msg)
                current_dst[key] = current_src[key]
            else:
                if (isinstance(current_src[key], dict) and
                    isinstance(current_dst[key], dict)):
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst

if __name__ == '__main__':
    def test():
        """Test if it works.
        """
        dst = dict(a=1, b=2, c=dict(ca=31, cc=33, cd=dict(cca=1)), d=4, f=6)
        src = dict(b='u2', c=dict(cb='u32', cd=dict(cda=dict(cdaa='u3411',
                                                            cdab='u3412'))),
                   e='u5')
        recursiveupdate(dst, src)
        import doctest
        doctest.testmod()
