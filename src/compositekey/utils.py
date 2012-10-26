__author__ = 'aldaran'

import re
from django.db.models import Model
P = re.compile("-('([^']+|'')*'|)")

__all__ = ["assemble_pk", "disassemble_pk", "assemble_key"]

def dimention_list_generator(l, size):
    i = iter(l)
    for x in xrange(min(len(l), size)):
        yield i.next()
    for i in xrange(size - len(l)):
        yield


def assemble_pk(*parts):
    if None in parts:return None
    return assemble_key(*[value.pk if isinstance(value, Model) else value for value in parts])

def assemble_key(*parts):
    return "-".join(["'%s'" % (str(p) if not isinstance(p, (str, unicode)) else p).replace("'", "''") if p is not None else '' for p in parts])

def disassemble_pk(key, length=None):
    key = str(key) if key is not None and not isinstance(key, (str, unicode)) else key
    if key is None or key.count("'") % 2 == 1:
        results = tuple()
    else:
        results = tuple([x[0][1:-1].replace("''", "'") if x[0] else None for x in P.findall("-"+key)])
    if length > 0 and len(results) != length:
        results = tuple(dimention_list_generator(results, length))
    return results
