# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:57:45 2023

@author: trist
"""
import os
from math import factorial, comb, prod
from concurrent.futures import ProcessPoolExecutor

import sympy as sym
from sympy import symbols, Wild
from sympy.core.numbers import Number as SympyNumber
from sympy.core.add import Add as SympyAdd
from sympy.core.mul import Mul as SympyMul
from sympy.functions.elementary.exponential import exp as sympyexp
from sympy import apart
import numpy as np


def worker(term):
    """
    Worker function for the conversion.
    """
    if isinstance(term, SympyAdd):
        ts = []
        for term1 in term.make_args(term):
            ts.append(convert_term(term1))
        return tuple(ts)
    else:
        return (convert_term(term),)


def parallel_inverse_lb_and_save(pf):
    """
    In parallel compute the inverse Laplace-Borel transform.
    The multiprocessing logic will now be inside a main block.
    """
    # Ensure the following code only runs when the script is executed directly.
    result = []
    if False:
        
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Pass the worker function to the executor map
            for r in executor.map(worker, pf):
                result.extend(r)
        return tuple(result)
    else:
        result = []
    
        # Serial loop through pf and apply the worker function
        for term in pf:
            r = worker(term)
            result.extend(r)
        
        return tuple(result)
        

def convert_gs_to_time(g):
    """
    Takes the list of generating series and returns the associated time
    function.
    """
    gs_pf = sympy_partfrac_here(g)
    
    time_terms = {}
    for key, pf in gs_pf.items():
        # Pickle the SymPy versions.
        # with open(f"quad_cube_y{key+1}_partfrac_symbolic.txt", "wb") as f_sym:
        #     pkl.dump(tuple(pf), f_sym)
        
        time_terms[key] = parallel_inverse_lb_and_save(pf)
        
        # with open(f"quad_cube_y{key+1}_volt_sym.txt", "wb") as f_sym:
        #     pkl.dump(list_serial, f_sym)
    
    return time_terms


def partial_parallel(term, x):
    """
    Decompose a single term into partial fractions and return the simplified terms.
    """
    pf_terms = apart(term.simplify(), x)  # Decompose the term
    separated = SympyAdd.make_args(pf_terms)    # Make individual fraction terms
    return [i.simplify() for i in separated]  # Return simplified fractions


# Helper function to be used in ProcessPoolExecutor
def partial_parallel_wrapper(term, x):
    """
    Wrapper for partial_parallel function to make it pickleable in multiprocessing.
    """
    return partial_parallel(term, x)


def sympy_partfrac_here(g):
    """
    Function to decompose terms into partial fractions using parallel processing.
    """
    x = symbols('x0')  # Define the symbolic variable
    storage_of_terms = {}
    cpu_cnt = os.cpu_count()  # Get the CPU count for parallel processing
    
    if isinstance(g, list):
        print("Not good behaviour in responses.sympy_partfrac_here, combining all terms into first gs")
        g = {0: g}
    
    for index, gs in g.items():
        individual_storage = []

        # if len(gs) < cpu_cnt:  # If the number of terms is less than CPU count, process sequentially
        if True:  # If the number of terms is less than CPU count, process sequentially
            for term in gs:
                individual_storage.extend(partial_parallel(term, x))
        else:
            # Use ProcessPoolExecutor for parallel processing
            with ProcessPoolExecutor(max_workers=cpu_cnt) as executor:
                # Pass the wrapper function to executor.map
                results = executor.map(partial_parallel_wrapper, gs, [x]*len(gs))  # Pass `x` for each term
                for r in results:
                    individual_storage.extend(r)  # Extend the storage with the results
        
        storage_of_terms[index] = individual_storage  # Store the results for the index
    
    return storage_of_terms


# =============================================================================
# above from impulse.py
# =============================================================================

def to_fraction(terms):
    """
    This converts from the array form of the generating series to the
    fraction form, so they can be sovled by a partial fraction calculator.
    
    The arive herer in "tuple form"
    """
    x0, x1 = symbols("x0 x1")
    output_list = []
    for term in terms:
        top_row = term[1][0].astype(dtype="O")
        bottom_row = term[1][1]
        top_row[np.equal(top_row, 0)] = x0
        top_row[np.equal(top_row, 1)] = x1
            
        numerator = prod(top_row)
        denominator = prod([(1 + i*x0) for i in bottom_row])
        
        output_list.append(term[0] * numerator / denominator)
    
    return output_list


def step_input(scheme, amplitude=1):
    """
    Converts the generating series to have a step input.
    """

    step_gs = []
    for term in to_fraction(scheme):
        step_gs.append(term.subs({symbols("x1"): amplitude * symbols("x0")}))
        
    return step_gs


def gwn_response(scheme, sigma=1):
    """
    Calculates the GWN response given an input generating series.
    """
    raise NotImplementedError("This hasnt been generalised to gs type")
    gwn = []
    # This first section of the for-loop is getting the terms of the desired
    # form, as many will be reduced to zero.
    for coeff, term in scheme:
        numerator = term[0]
        count_1s = 0
        for val in numerator:
            if val == 0:
                if (count_1s % 2 == 0):
                    continue
                else:
                    count_1s = 0
                    break
            if val == 1:
                count_1s += 1
            
        else:
            if (count_1s % 2 != 0):
                continue
            
            count_1s = 0
            new_term = np.zeros((2, 1))
            for i, val in enumerate(numerator):
                if val == 0:
                    temp = term[:, i].reshape(2, 1)
                    new_term = np.hstack([new_term, temp])
                    continue
                
                elif val == 1 and count_1s == 1:
                    count_1s = 0
                    coeff *= ((sigma ** 2) / 2)
                    temp = term[:, i-1].reshape(2, 1)
                    temp[0, 0] = 0
                    new_term = np.hstack([new_term, temp])
                    continue
                
                elif val == 1 and count_1s == 0:
                    count_1s = 1
                    continue
                
                else:
                    raise ValueError("Code should not be here.")
            gwn.append((coeff, new_term))
    
    return to_fraction(gwn)
            

def impulse(scheme, amplitude=1):
    """
    Defined in "Functional Analysis of Nonlinear Circuits- a Generating Power
    Series Approach".
    
    This is used if the generating series have already been expanded. For
    efficiency use impulse_from_iter().
    """
    x0, x1 = symbols("x0 x1")

    imp = []
    for coeff, term in scheme:
        x0_storage = []
        for i, x_i in enumerate(term[0, :]):
            if x_i == x1:
                if all(np.equal(term[0, i:], x1)):
                    n = term.shape[1] - i
                    frac = (
                        coeff/factorial(int(n)) / (1+term[1, i]*symbols("x0"))
                    )
                    if x0_storage:
                        for x0_term in x0_storage:
                            frac *= x0_term
                    imp.append(amplitude**n * frac)
                break
            elif x_i == x0:
                x0_storage.append(symbols("x0") / (1+term[1, i]*symbols("x0")))
            else:
                raise ValueError("Unknown term in 0th row.")

    return imp


def convert_term(term):
    """
    Checks against each of the required forms, if the correct form is
    identified the inverse laplace borel transform of it is returned. If the
    term fits no form, an error it raised.
    """
    func_pairs = (
        (is_exponential_form, lb_exponential),
        (is_unit_form,        lb_unit),
        (is_polynomial_form,  lb_polynomial),
        (is_cosine_form,      lb_cosine),
    )
    
    for (form_test, converter) in func_pairs:
        if form_test(term):
            return converter(term)
    else:
        raise TypeError(f"Term is of an unknown form.\n\n{term}")
    
    
def inverse_lb(sum_of_fractions):
    """
    Converts the partial fractions into the time domain.
    
    There are two cases that need to be analysed here. If the term is type
    SympyAdd, we need to get each term in the addition and analyse these
    separately. Otherwise, the term is passed in as usual.
    """
    ts = []
    for term in sum_of_fractions:
        if isinstance(term, SympyAdd):
            for term1 in term.make_args(term):
                ts.append(convert_term(term1))
        else:
            term_ts = convert_term(term)
            ts.append(term_ts)
        
    return ts


def is_unit_form(term):
    """
    Determines whether the term is of unit form, both sympy Float and
    sympy Integer inherit from sympy Number.
    """
    return isinstance(term, (SympyNumber, int, float))


def lb_unit(term):
    """
    
    """
    return term


def is_polynomial_form(term):
    """
    Tests whether the term is of polynomial form.
    """
    if is_unit_form(term):
        return False
    
    x0 = symbols("x0")
    a = Wild("a", exclude=[x0, 0])
    n = Wild("n")
        
    polynomial_form = a * x0 ** n
    
    match = term.match(polynomial_form)
    if match:
        if not match[n].is_integer:
            return False
    
    return match


def lb_polynomial(term):
    """
    a * x ** n
    """
    x0, t = symbols("x0 t")
    a = Wild("a", exclude=[x0, 0])
    n = Wild("n", exclude=[0])
        
    polynomial_form = a * x0 ** n
    
    match = term.match(polynomial_form)
    n = match[n]
    a = match[a]
    
    return (a / sym.factorial(n)) * t ** n


def is_exponential_form(term):
    """
    Tests whether the term is of exponential form.
    
    This method of reducing all the denominator coefficients and only matching
    the crucial part is much faster.
    """
    if is_unit_form(term):
        return False
    
    x0 = symbols("x0")

    b = Wild("b", exclude=[x0])
    c = Wild("c", exclude=[x0])

    n = Wild("n")
        
    a, denom = term.as_numer_denom()
    
    if x0 in a.free_symbols:
        return False
    
    den_args = SympyMul.make_args(denom)
    den_coeffs = 1
    crucial = None
    for den_arg in den_args:
        if x0 in den_arg.free_symbols:
            if not crucial:
                crucial = den_arg
            else:
                return False
        else:
            den_coeffs *= den_arg
    
    try:
        if x0 in den_coeffs.free_symbols:
            return False
    except AttributeError:
        pass
        
    # Match the crucial part of the denominator.
    denom_form = (b + c * x0) ** n
    match = crucial.match(denom_form)
        
    if match:
        if not match[n].is_integer:
            print(
                "responses.is_exponential_form:",
                "failing because n is not an integer"
            )
            return False
    
    return bool(match)


def lb_exponential(term):
    """
    a / (den_coeffs * (b + c*x0) ** n)
    """
    x0, t = symbols("x0 t")

    b = Wild("b", exclude=[x0])
    c = Wild("c", exclude=[x0])
    
    n = Wild("n")
    
    a, denom = term.as_numer_denom()
    
    den_args = SympyMul.make_args(denom)
    den_coeffs = 1
    for den_arg in den_args:
        if x0 in den_arg.free_symbols:
            crucial = den_arg
        else:
            den_coeffs *= den_arg

    denom_form = (b + c * x0) ** n
    match = crucial.match(denom_form)

    b = match[b]
    c = -match[c]
    n = match[n]
    
    coeff1 = a / (b ** n * den_coeffs)
    coeff2 = c / b
    
    ts = 0
    for i in range(n):
        ts += (comb(n-1, i) / sym.factorial(i)) * (coeff2 * t) ** i
    ts *= (coeff1 * sympyexp(coeff2 * t))

    return ts


def is_cosine_form(term):
    """
    Tests whether the term is of cosine form.
    """
    print("COSINE IS SLOW")
    if is_unit_form(term):
        return False
    
    x0 = symbols("x0")
    a = Wild("a", exclude=[x0, 0])
    b = Wild("b", exclude=[x0, 0])
    c = Wild("c", exclude=[x0, 0])
    n = Wild("n", exclude=[x0, 0])
    
    cosine_form = a * (b + c*x0**2) ** -n
    
    match = term.match(cosine_form)
    
    if match:
        if not match[n].is_integer:
            return False
    
    return match


def lb_cosine(term):
    """
    a * (b + c*x**2) ** -1
    """
    print("COSINE IS SLOW")
    x0, t = symbols("x0 t")
    a = Wild("a", exclude=[x0, 0])
    b = Wild("b", exclude=[x0, 0])
    c = Wild("c", exclude=[x0, 0])
    n = Wild("n", exclude=[x0, 0])
    
    cosine_form = a * (b + c*x0**2) ** -n
    
    match = term.match(cosine_form)

    a = match[a]
    b = match[b]
    c = match[c]
    n = match[n]
    
    coeff1 = a / b**n
    coeff2 = sym.sqrt(c / b)
    
    return coeff1 * sym.cos(coeff2 * t)


def time_function(time_domain):
    """
    Get a function of the response wth respect to time.
    
    """
    return sym.lambdify(symbols('t'), time_domain)