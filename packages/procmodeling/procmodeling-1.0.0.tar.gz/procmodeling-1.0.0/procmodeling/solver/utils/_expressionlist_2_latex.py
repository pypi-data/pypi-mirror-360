import re
import sympy as sp

def _expressionlist_2_latex(
        left_side,
        right_side,
        begin = ''
        ) -> str:

    '''
    Transform a list os equation expressions on LaTeX code.

    IMPUT:
    Can be a list of strings or a list of lists with the equation expressions:
    `left_side = [expression1, expression2, [expression3, expression4], ...]`
    `right_side = [expression1, expression2, [expression3, expression4], ...]`

    `left_side` and `right_side` must be the same shape.

    `expressions` must be of `str` type that can be processed by the sympy.sympify() function
    '''

    S = sp.Symbol('S')

    equations_text = ''

    msg = 'the left_side and right_side are not the same length'
    assert len(left_side)==len(right_side), msg
    
    for arg in zip(left_side, right_side):
        if isinstance(arg[0], str) and isinstance(arg[1], str):
            left_text = arg[0]
            right_text = arg[1]
            # Replace "dy/dt[i]" instances to "dy_i/dt"
            left_text = re.sub(r'dy/dt\[(\d+)\]', r'dy_\1/dt', left_text)
            # Replace "[i]" instances to "_i"
            left_text = re.sub(r'\[(\d+)\]', r'_\1', left_text)
            right_text = re.sub(r'\[(\d+)\]', r'_\1', right_text)
            
            # Converts an arbitrary expression to a type that can be used inside SymPy
            try:
                left_text = sp.sympify(left_text, rational=False, locals={'S': S})
                right_text = sp.sympify(right_text, rational=False, locals={'S': S})
            except TypeError as e:
                print(e.__class__.__name__,':',e)
                print(e.__cause__)
            except ValueError as e:
                print(e.__class__.__name__,':',e)
                print(e.__cause__)
            
            # Create the SymPy equation object
            equation = sp.Eq(left_text, right_text)
            # Converts SymPy object to latex expression
            equation = sp.latex(equation, mul_symbol='dot')
            
            equations_text += '$' + begin + ' ' + equation + '$ \n '

        elif isinstance(arg[0], (list, tuple)) and isinstance(arg[1], (list, tuple)):
            equations_text += _expressionlist_2_latex(arg[0], arg[1])

        else:
            print('Error _expressionlist_2_latex: `left_side` and `right_side` must have the same shape.')
            print('left_side:', arg[0])
            print('right_side:', arg[1])

    return equations_text