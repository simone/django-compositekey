__author__ = 'fabio'

from django.conf import settings

__all__ = ["assemble_pk", "disassemble_pk", "SEP", "ESCAPE_CHAR"]

SEP, ESCAPE_CHAR, NONE_CHAR  = getattr(settings, "COMPOSITE_PK_SEPARATOR_ESCAPE", '-.N')

def assemble_pk(*values):
    result = ''
    for value in values:

        if not value == None:
            value = str(value)

            for special_char in (ESCAPE_CHAR, SEP, NONE_CHAR):
                if special_char in value:
                    value = value.replace(special_char, ESCAPE_CHAR+special_char)
        else:
            value = NONE_CHAR

        result = result + value + SEP

    return result[:-1]

def disassemble_pk(comp_pk):
    """
    >>> disassemble_pk(assemble_pk("1", "2"))
    ['1', '2']
    """

    if comp_pk is not None:
        comp_pk = str(comp_pk)
        result = []
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
                    result.append(None)
                else:
                    value = value.replace(ESCAPE_CHAR+NONE_CHAR, NONE_CHAR)
                    result.append(value)
                curr_index = index+1

            index = index+1
        else:
            value = comp_pk[curr_index:].replace(ESCAPE_CHAR+SEP, SEP)
            value = value.replace(2*ESCAPE_CHAR, ESCAPE_CHAR)

            if value == NONE_CHAR:
                result.append(None)
            else:
                value = value.replace(ESCAPE_CHAR+NONE_CHAR, NONE_CHAR)
                result.append(value)

        return result
    return []