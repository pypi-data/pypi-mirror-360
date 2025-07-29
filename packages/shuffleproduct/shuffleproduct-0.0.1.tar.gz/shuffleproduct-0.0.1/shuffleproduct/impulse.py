from collections import defaultdict
from operator import itemgetter
from itertools import product

import numpy as np
from sympy import symbols, factorial

from . import shuffle as shfl


def remove_nonimp(terms):
    """
    Removes all the terms that have an x0 after an x1.
    """
    if not terms:
        return []
    
    x0, x1 = symbols("x0 x1")

    store = []
    for term in terms:
        has_been_x1 = False
        for val in term.words:
            if val == x1:
                has_been_x1 = True
                continue
            elif val == x0 and (not has_been_x1):
                continue
            else:
                break
        else:
            store.append(term)
            
    return store


def check_n_x1s_less_than_iter_depth(terms, iter_depth):
    """
    This is used as an early elimination tool. If the generating series
    produced are going to be eliminated anyway, you may as well not calculate
    the expensive shuffle product.
    """
    count = 0
    for term in terms:
        count += term.n_excites
    
    return count <= (iter_depth + 1)


def iterate_quad_cubic(g0, mults, iter_depth):
    """
    A very hastily written iterative expansion of a SDOF oscillator with
    quadratic and cubic nonlinearities.
    
    This function is reliant on global variables, be careful! It also isn't
    generalisable at all, but it's what we need for our specific example.
    
    Should write this so the function takes in (m, c, k1) and then determines
    the number of nonlinearities by the size of the list passed in.
    """
    mult_quad, mult_cube = mults
    
    term_storage = defaultdict(list)
    term_storage[0].append(g0)
    
    term_storage_quad = defaultdict(list)
    term_storage_cube = defaultdict(list)
    
    for depth in range(iter_depth):
        for part in shfl.partitions(depth, 2):
            terms = itemgetter(*part)(term_storage)
            for in_perm in product(*terms):
                if check_n_x1s_less_than_iter_depth(in_perm, iter_depth):
                    term_storage_quad[depth+1].extend(shfl.nShuffles(*in_perm))
        
        term_storage_quad[depth+1] = shfl.collect(term_storage_quad[depth+1])
        term_storage_quad[depth+1] = remove_nonimp(term_storage_quad[depth+1])
        
        for part in shfl.partitions(depth, 3):
            terms = itemgetter(*part)(term_storage)
            for in_perm in product(*terms):
                if check_n_x1s_less_than_iter_depth(in_perm, iter_depth):
                    term_storage_cube[depth+1].extend(shfl.nShuffles(*in_perm))
        term_storage_cube[depth+1] = shfl.collect(term_storage_cube[depth+1])
        term_storage_cube[depth+1] = remove_nonimp(term_storage_cube[depth+1])
    
        # After the shuffles for this iteration's depth have been caluclated,
        # prepend the multiplier to each term.
        for gs_term in term_storage_quad[depth+1]:
            gs_term.prepend_multiplier(mult_quad)
        term_storage[depth+1].extend(term_storage_quad[depth+1])
        
        for gs_term in term_storage_cube[depth+1]:
            gs_term.prepend_multiplier(mult_cube)
        term_storage[depth+1].extend(term_storage_cube[depth+1])
        
        term_storage[depth+1] = shfl.collect(term_storage[depth+1])
    
    return g0.handle_output_type(term_storage, tuple)


def impulsehere(terms, amp, iter_depth):
    """
    
    """
    imp = defaultdict(list)
    
    x0_sym = symbols("x0")
    if terms[0][1].dtype == object:
        x0, x1 = symbols("x0 x1")
    else:
        x0, x1 = 0, 1
    
    for coeff, term in terms:
        x0_storage = []
        for i, x_i in enumerate(term[0, :]):
            if x_i == x1:
                if all(np.equal(term[0, i:], x1)):
                    n = term.shape[1] - i
                    frac = (
                        (coeff / factorial(int(n))) / (1 - term[1, i]*x0_sym)
                    )
                    if x0_storage:
                        for x0_term in x0_storage:
                            frac *= x0_term
                    imp[n].append(amp**n * frac)
                break
            elif x_i == x0:
                x0_storage.append(x0_sym / (1 - term[1, i]*x0_sym))
            else:
                raise ValueError("Unknown term in 0th row.")

    return {key: imp[key+1] for key in range(iter_depth+1)}
