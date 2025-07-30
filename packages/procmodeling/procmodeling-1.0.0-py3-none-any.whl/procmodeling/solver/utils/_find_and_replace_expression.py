import re

def _find_and_replace_expression(old, new, expres):
    '''
    Replace only the `old` string in `expres` that are around operators `(+,\\,-,*,%,=)`, 
    whitespace (" ") or are at the end/beginning of the string

    Returns `None` if not find `old`
    '''
    l_pattern = r'(?:(?<=^)|(?<=[+\-*/%=\s(){}$]))'
    r_pattern = r'(?:(?=$)|(?=[+\-*/%=\s(){}$]))'

    if re.search(l_pattern + old + r_pattern, expres):
        return re.sub( l_pattern + old + r_pattern, new, expres)
    else:
        return None