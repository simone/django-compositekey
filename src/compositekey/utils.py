__author__ = 'fabio'

from django.conf import settings

__all__ = ["assemble_pk", "disassemble_pk", "SEP", "ESCAPE_CHAR", "NONE_CHAR"]

SEP, ESCAPE_CHAR, NONE_CHAR = getattr(settings, "COMPOSITE_PK_SEPARATOR_ESCAPE", '-.N')


def assemble_pk(*values):
    if len(values) == 1:
        return values[0]

    # No ammissible multiplekey with a Null part (blank values are ok)
    # because django features (ex inline) check if a key is None for new forms
    for val in values:
        if val is None:
            return None

    result = ''
    for value in values:

        if not value == None:
            value = unicode(value)

            for special_char in (ESCAPE_CHAR, SEP, NONE_CHAR):
                if special_char in value:
                    value = value.replace(special_char, ESCAPE_CHAR+special_char)
        else:
            value = NONE_CHAR

        result = result + value + SEP

    return result[:-1]

def dimention_list_generator(l, size):
    i = iter(l)
    for x in xrange(min(len(l), size)):
        yield i.next()
    for i in xrange(size - len(l)):
        yield

def disassemble_pk(comp_pk, length=None):
    """
    >>> disassemble_pk(assemble_pk("1", "2"))
    ['1', '2']
    """
    results = []
    if comp_pk is not None:
        comp_pk = unicode(comp_pk)
        curr_index = 0
        index = 0
        while index < len(comp_pk):

            if comp_pk[index] == ESCAPE_CHAR:
                if comp_pk[index+1] in (SEP, ESCAPE_CHAR, NONE_CHAR):
                    index = index+2
                    continue

            if comp_pk[index] == SEP:
                value = comp_pk[curr_index:index].replace(ESCAPE_CHAR+SEP, SEP)
                value = value.replace(2*ESCAPE_CHAR, ESCAPE_CHAR)

                if value == NONE_CHAR:
                    results.append(None)
                else:
                    value = value.replace(ESCAPE_CHAR+NONE_CHAR, NONE_CHAR)
                    results.append(unicode(value))
                curr_index = index+1

            index = index+1
        else:
            value = comp_pk[curr_index:].replace(ESCAPE_CHAR+SEP, SEP)
            value = value.replace(2*ESCAPE_CHAR, ESCAPE_CHAR)

            if value == NONE_CHAR:
                results.append(None)
            else:
                value = value.replace(ESCAPE_CHAR+NONE_CHAR, NONE_CHAR)
                results.append(unicode(value))

    if length > 0:
        results = list(dimention_list_generator(results, length))
    return results