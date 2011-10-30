__author__ = 'fabio'

from django.conf import settings

__all__ = ["assemble_pk", "disassemble_pk"]

SEP, ESCAPE_CHAR  = getattr(settings, "COMPOSITE_PK_SEPARATOR_ESCAPE", '-.')

def assemble_pk(*values):
    if min(values) is None:
        return None

    result = ''
    for value in values:
        value = str(value) if value else ''
        
        if ESCAPE_CHAR in value:
            value = value.replace(ESCAPE_CHAR, 2*ESCAPE_CHAR)
        if SEP in value:
            value = value.replace(SEP, ESCAPE_CHAR+SEP)
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
                if comp_pk[index+1] in (SEP, ESCAPE_CHAR):
                    index = index+2
                    continue

            if comp_pk[index] == SEP:
                value = comp_pk[curr_index:index].replace(ESCAPE_CHAR+SEP, SEP)
                value = value.replace(2*ESCAPE_CHAR, ESCAPE_CHAR)
                result.append(value)
                curr_index = index+1

            index = index+1
        else:
            value = comp_pk[curr_index:].replace(ESCAPE_CHAR+SEP, SEP)
            value = value.replace(2*ESCAPE_CHAR, ESCAPE_CHAR)
            result.append(value)

        return result
    return []

if __name__ == '__main__':

    #'ab', 'a_b', 'a|_b', 123, 'a_', 'b|', 'c|_', '_', '|', '|_', '_|', '', None, 'd|_'
    params = ['ab', 'a'+SEP+'b', 'a'+ESCAPE_CHAR+SEP+'b', '123', 'a'+SEP, 'b'+ESCAPE_CHAR, 'c'+ESCAPE_CHAR+SEP, SEP, ESCAPE_CHAR, ESCAPE_CHAR+SEP, SEP+ESCAPE_CHAR, '', None, 'd'+ESCAPE_CHAR+SEP]

    encoded_pk = assemble_pk(*params)
    decoded_pk = disassemble_pk(encoded_pk)

    print encoded_pk
    print params
    print decoded_pk

    #Fallisce per il None
    #assert params == decoded_pk
    assert disassemble_pk(assemble_pk("1", "2")) == ['1', '2']

    assert '' == assemble_pk(None), "None non gestito correttamente"
    assert None == disassemble_pk(None), "None non gestito correttamente"
    assert [''] == disassemble_pk(''), "Blank non gestito correttamente"