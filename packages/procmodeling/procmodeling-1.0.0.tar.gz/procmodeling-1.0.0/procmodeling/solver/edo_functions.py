import numpy as np
import pandas as pd
import re
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.integrate import solve_ivp
from scipy.optimize import differential_evolution

from .utils import _plot_text, _is_number, _find_and_replace_expression, _expressionlist_2_latex

def _remove_comments(text:str) -> str:
    """
    Remove comments (starting with '#') from a multi-line string.
    """
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = line.split('#', 1)[0].rstrip()
        if cleaned_line:  # opcional: remove linhas vazias
            cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)


class edo_functions:

    def __init__(self, name:str, verbose:bool=True):

        self.verbose = verbose
        
        self.diff_equations = {}
        self.expressions = {}
        self.params = {}
        self.lines = []

        filepath = Path(name)
        if filepath.is_file():
            self._read_txt(name)
            print('edo_functions: Document was read')
        else:
            self._read_docstr(name)
            print('edo_functions: Docstring was read')


    def _read_txt(self, filename:str):
        with open(filename, 'r', encoding="utf-8") as file:
            self.lines = file.readlines()
        self._read_expressions()

    def _read_docstr(self, docstr:str):
        self.lines = docstr.split('\n')
        self._read_expressions()


    def _read_expressions(self):
        diff_equations = {}
        expressions = {}
        params = {}
        for line in self.lines:
            # Remove spaces at the beginning and at the end of the string
            line = line.strip()

            if not(line.startswith('#')):
                # Read ODE. Format: dydt = f(y, t, params)
                if line.startswith('dydt'):
                    pattern = re.search(r'dydt\[(\d+)\]', line) # the "dydt[i]" pattern
                    if pattern:
                        diff_equations[int(line[5])] = line.split('=')[1].strip()
                # Read other expressions
                elif ('=' in line):
                    cleaned_line = _remove_comments(line)
                    key, value = cleaned_line.split('=')
                    if _is_number(value):
                        params[key.strip()] = float(value.strip())
                    else:
                        expressions[key.strip()] = value.strip()
                    # key, value = line.split('=')
                    # if _is_number(value):
                    #     params[key.strip()] = float(value.strip())
                    # else:
                    #     expressions[key.strip()] = value.strip()

        self.diff_equations = diff_equations
        self.expressions = expressions
        self.params = params

        if self.verbose:
            self.show_equations()




    def show_equations(self):
        laxtext = ' '
        if self.diff_equations:
            # Add the diff_equations in laxtext
            left_text = [f'dy_{i}/dt' for i in self.diff_equations.keys()]
            laxtext += _expressionlist_2_latex(left_text, self.diff_equations.values(), begin=r'\Longrightarrow')
            
            # highlight in bold the keys of "self.expressions"
            for var in self.expressions.keys():
                # The character "_i" will be replaced by "{i}". i.e. "A_i" to "A{i}"
                var2 = re.sub(r'_(\w+)', r'_{\1}', var)
                var2 = re.sub(r'(?<=[a-zA-Z])(\d+)(?![a-zA-Z])', r'_{\1}', var2)
                check_if_exists = _find_and_replace_expression(re.escape(var2), rf'\\mathbf{{{var2}}}', laxtext)
                laxtext = check_if_exists if check_if_exists else laxtext

            # Add the expressions in laxtext
            if self.expressions:
                laxtext += '\n '
                laxtext += _expressionlist_2_latex(self.expressions.keys(), self.expressions.values(), begin=r'\Rightarrow')
            # Add the paramns in laxtext
            if self.params:
                laxtext += '\n'+ r'$\it{Parameters:}$' + '\n '
                right_text = list(map(str, self.params.values()))
                laxtext += _expressionlist_2_latex(self.params.keys(), right_text, begin=r'\rightarrow')
        else:
            print('No equations found')

        _plot_text(laxtext)




    def _replace_expressions(self):
        
        # Replace the right side variables in "self.expressions" that are not parameters.
        check = [True]
        repl_expression = self.expressions.copy()
        while any(check):
            check=[]
            for var1 in self.expressions.keys():
                for var2 in self.expressions.keys():
                    if not ( var1 == var2 ):
                        var_in_expr = _find_and_replace_expression(
                            var2, 
                            r'(' + self.expressions[var2] + r')', 
                            repl_expression[var1]
                            )
                        if var_in_expr:
                            check+=[True]
                            repl_expression[var1] = var_in_expr
                        else:
                            check+=[False]
        # Replace the right side variables in "self.diff_equations" that are not parameters.
        repl_equations = self.diff_equations.copy()
        for i in repl_equations.keys():
            for var, expr in repl_expression.items():
                check_if_exists = _find_and_replace_expression(var, r'(' + expr + r')', repl_equations[i])
                repl_equations[i] = check_if_exists if check_if_exists else repl_equations[i]
        
        #####################################################
        # display(list(repl_equations.values()), self.params)
        #####################################################
        self._repl_equations = repl_equations

    
    
    # Def method that will create the solve_ivp default function using
    # the "repl_equations" strings and "self.params" dict
    def _call_function(self, equations:list, params:dict):
        # Declare predefined functions
        predefine_func = {
            # Exponents and logarithms
            'sqrt':np.sqrt,
            'exp':np.exp,
            'log':np.log,
            'log10':np.log10,
            'log2':np.log2,
            'log1p':np.log1p,
            # Trigonometric functions
            'cos':np.cos,
            'sen':np.sin,
            'tan':np.tan,
            'arcsin':np.arcsin,
            'asin':np.asin,
            'acos':np.acos,
            'arccos':np.arccos,
            'arctan':np.arctan,
            # Hyperbolic functions
            'cosh':np.cosh,
            'senh':np.sinh,
            'tanh':np.tanh,
        }

        def ode_system(t, y):
            dydt = []
            for eq in equations:
                dydt.append(eval(eq, {**params, 'y': y, 't': t, **predefine_func}))
            return dydt
        
        return ode_system





    def solve(self,
            t_span:list, 
            y0:list, 
            t_eval= None,
            method:str = 'RK45',
            show_plot = True,
            _params = None,
            _data = None,
            _var_columns = None,
            _time_column = None
            ):
        
        self._replace_expressions()
        _params = self.params if _params == None else _params
        self.function = self._call_function( self._repl_equations.values(), _params )

        n_points = 100
        if not(t_eval):
            t_eval = np.linspace(t_span[0], t_span[1], n_points)

        self.result = solve_ivp(self.function, 
                                t_span,
                                y0,
                                method = method,
                                t_eval = t_eval,
                                )
        
        if show_plot == True:
            self._plot_results(_data, _var_columns, _time_column)

    def _plot_results(self, data, var_columns, time_column):
        var_count = len(self.result.y)
        if (data is None) or (var_columns is None) or (time_column is None):
            var_columns = [None]*var_count

        fig, axs = plt.subplots(1, var_count, figsize=[2.5*var_count, 2.5])
        
        for i, var in enumerate(var_columns):
            axs[i].plot(self.result.t, self.result.y[i], color='black')
            axs[i].set_title(f'Variable {i}')
            axs[i].set_xlabel('time')
            axs[i].set_ylabel(f'Variable {i}')
            if var:
                axs[i].scatter(data[time_column], data[var], color='black')
        
        fig.tight_layout()




    def optimize(self,
                data:pd.DataFrame,
                initial_values_columns:list,
                target_values_columns:list,
                time_column:str,
                bounds:dict,
                method:str = 'differential_evolution',
                solver_method = 'RK45',
                score:str = 'rmse',
                max_iter_DE = 100,# 100
                popsize_DE = 15 #15

                ):

        self._optimize_data = data
        self._optimize_initial_values_columns = initial_values_columns
        self._optimize_target_values_columns = target_values_columns
        self._optimize_time_column = time_column
        self._optimize_bounds = bounds
        self._optimize_solver_method = solver_method
        self._optimize_score = score

        fobj = self._call_objective_function()

        pbar = tqdm(total=max_iter_DE)
        def update_progress(xk, convergence):
            pbar.update(1)

        if method == 'differential_evolution':
            opt_result = differential_evolution(fobj, list(bounds.values()), 
                                        popsize=popsize_DE, maxiter=max_iter_DE,
                                        callback=update_progress,
                                        # strategy='best1bin', polish=False
                                        )

        self.opt_params = dict(zip( bounds.keys(), opt_result.x ))
        self.opt_result = opt_result

        # Create a dictionary with the parameters:
        dict_params = self.opt_params.copy()
        # put the parameter values ​​that are not in "bounds"
        for p in set(self.params.keys()) - set(bounds.keys()):
            dict_params[p] = self.params[p]
        #Solve eache initial condition
        for indexes in self._optimize_cond0indexes:
            data_cond0 = data.loc[indexes]
            times = data_cond0[time_column].values
            cond0 = data.loc[indexes[0], initial_values_columns].values

            # Solve the edo function
            t_span = (times.min(), times.max())
            y0 = cond0
            _plot_text(f'Initial Cond. → {y0}')
            self.solve(
                t_span, y0,
                _params = dict_params,
                _data = data_cond0,
                _var_columns = target_values_columns,
                _time_column = time_column
                )

    def _call_objective_function(self):

        data = self._optimize_data
        initial_values_columns = self._optimize_initial_values_columns
        bounds = self._optimize_bounds
        solver_method = self._optimize_solver_method
        time_column = self._optimize_time_column

        target_values_columns = self._optimize_target_values_columns
        score = self._optimize_score
        
        # Find all initial conditions in "data"
        initial_conditions = data[initial_values_columns].values
        initial_conditions = np.array(list({tuple(x) for x in initial_conditions}), dtype=object)

        self._optimize_cond0indexes = []
        for cond0 in initial_conditions:
            # get the indexes of the rows with initial value conditions = "cond" (<1E-10)
            indexes = []
            for initial_v, i in zip(data[initial_values_columns].values, data.index):
                if (all(abs(initial_v - cond0)<1E-10)):
                    indexes.append(i)
            
            self._optimize_cond0indexes.append(indexes)

        def objective_function(params):
            # Create a dictionary with the parameters:
            dict_params = dict(zip( bounds.keys(), params ))
            # put the parameter values ​​that are not in "bounds"
            for p in set(self.params.keys()) - set(bounds.keys()):
                dict_params[p] = self.params[p]
            # define edo and solve:
            edo_func = self._call_function( self._repl_equations.values(), dict_params )

            error = 0
            for indexes in self._optimize_cond0indexes:

                data_cond0 = data.loc[indexes]
                times = data_cond0[time_column].values
                cond0 = data.loc[indexes[0], initial_values_columns].values

                # Solve the edo function
                t_span = (times.min(), times.max())
                y0 = cond0
                t_eval = times
                result = solve_ivp(edo_func, 
                                    t_span,
                                    y0,
                                    method = solver_method,
                                    t_eval = t_eval,
                                    )
                
                # get the error
                for i, var in enumerate(target_values_columns):
                    if var:

                        if score == 'rmse':
                            check_error = rmse( data_cond0[var].values, result.y[i])

                        if (check_error) and not(np.isnan(check_error)):
                            error += check_error
            return error

        return objective_function






import numpy as np
import pandas as pd

def _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred):
    '''
    input -> list, tupla, np.ndarray, pd.DataFrame
    '''
    
    if isinstance(y_true, pd.DataFrame):
        y_true = y_true.values.ravel()
    if isinstance(y_pred, pd.DataFrame):
        y_pred = y_pred.values.ravel()

    if isinstance(y_true, (list, tuple)):
        y_true = np.array(list(y_true))
    if isinstance(y_pred, (list, tuple)):
        y_pred = np.array(list(y_pred))

    if isinstance(y_true, np.ndarray) and isinstance(y_pred, np.ndarray):
        if (y_true.shape != y_pred.shape):
            y_true = y_true.ravel()
            y_pred = y_pred.ravel()
        
        msg = 'ERROR: The input data is not valid. `y_true` does not have the same shape as `y_pred`'
        if (y_true.shape != y_pred.shape): raise ValueError(msg)
        
    return y_true, y_pred


def c_coeff(y_true = 'class numpy.ndarray',
            y_pred = 'class numpy.ndarray'
            ): #https://www.sciencedirect.com/science/article/abs/pii/S0376738817311572?via%3Dihub
    '''
    Coeficiente proposto por Wessling et al (1997) (https://doi.org/10.1016/0376-7388(93)E0168-J)

    The neural network works predictively if C is smaller than 1. For C=l, the
    predicted permeability for an unknown polymer would be  equal to the average
    permeability of all polymers presented in the set (which is, in fact, useless).

    '''
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    
    denominador = sum(abs(y_true.mean() - y_true))
    if denominador!=0:
        return sum(abs(y_pred-y_true))/denominador
    else:
        return np.nan

def r2(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return 1 - np.sum(np.square(np.subtract(y_true, y_pred)))/np.sum(np.square(np.subtract(y_true, np.mean(y_true) )))

def neg_r2(y_true, y_pred):
    return -r2(y_true, y_pred)

def rmse(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return np.sqrt( np.sum(np.square(np.subtract(y_true, y_pred)))/len(y_true) )

def mape(y_true, y_pred):
    y_true, y_pred = _ensure_that_input_is_valid_data_for_metrics(y_true, y_pred)
    return np.sum( np.absolute( np.divide( np.subtract(y_true, y_pred), y_true) ))/len(y_true)