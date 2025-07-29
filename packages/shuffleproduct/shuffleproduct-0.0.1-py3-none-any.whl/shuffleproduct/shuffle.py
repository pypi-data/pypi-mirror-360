# -*- coding: utf-8 -*-
"""
Created on Thu May 11 17:10:37 2023

@author: trist
"""
from collections import defaultdict
from itertools import permutations, product
from operator import itemgetter
from typing import List, Tuple, Union
import functools
import copy

import numpy as np
from sympy import symbols

from .generating_series import GeneratingSeries as GS
from .responses import impulse


def shuffle_cacher(func):
    shuffle_cache = {}
    
    @functools.wraps(func)
    def wrapper(*args):
        # Sort the arguments to give ~2x cache hits.
        args = sorted(args, key=hash)
        
        key = tuple([hash(gs) for gs in args])
        coeff = 1
        for gs in args:
            coeff *= gs.coeff
        
        if key not in shuffle_cache:  # Store the result if unknown.
            result = func(*args)
            to_cache = copy.deepcopy(result)
            shuffle_cache[key] = (coeff, to_cache)
            return result
        
        else:  # Lookup and scale if known.
            prev_coeff, prev_result = shuffle_cache[key]
            
            if prev_coeff != coeff:
                scale = coeff / prev_coeff
                to_return = []
                for prev in copy.deepcopy(prev_result):
                    prev.scale_coeff(scale)
                    to_return.append(prev)
                return to_return
            else:
                return copy.deepcopy(prev_result)
    
    return wrapper


@shuffle_cacher
def binary_shuffle(gs1, gs2):
    """
    For the grid first index is number of reductions for gs2, second index is
    number of reductions of gs1).
    
    Reorder if statements so most likely is first.
        
    List and append, rather than np.hstack then stack at the end.
    """
    end1, gs1, gs1_len = gs1.get_end(gs1)
    end2, gs2, gs2_len = gs1.get_end(gs2)
    
    grid = defaultdict(list)
    
    for i1 in range(gs1_len+1):
        is_reducible1 = (i1 < gs1_len)
        if is_reducible1:
            g1 = gs1.get_term(i1)

        for i2 in range(gs2_len+1):
            is_reducible2 = (i2 < gs2_len)
            if is_reducible2:
                g2 = gs2.get_term(i2)

            if is_reducible1 and is_reducible2:
                gs1_reduct = gs1.reduction_term(g1, g2)
                gs2_reduct = gs1.reduction_term(g2, g1)
            
            elif is_reducible1 and not is_reducible2:
                gs1_reduct = gs1.reduction_term(g1, end2)
                
            elif not is_reducible1 and is_reducible2:
                gs2_reduct = gs1.reduction_term(g2, end1)
            
            current = grid[(i2, i1)]
            if not current:
                # Special case for first loop pass.
                grid[(0, 1)].append(gs1.first_term(gs1_reduct))
                grid[(1, 0)].append(gs1.first_term(gs2_reduct))
                continue
            
            for count, curr in collect_grid(current):
                if is_reducible1 and is_reducible2:
                    gs1.add_to_stack(grid[(i2, i1+1)], count, gs1_reduct, curr)
                    gs1.add_to_stack(grid[(i2+1, i1)], count, gs2_reduct, curr)

                elif is_reducible1 and not is_reducible2:
                    gs1.add_to_stack(grid[(i2, i1+1)], count, gs1_reduct, curr)

                elif not is_reducible1 and is_reducible2:
                    gs1.add_to_stack(grid[(i2+1, i1)], count, gs2_reduct, curr)
                    grid[(i2+1, i1)] = collect_grid(grid[(i2+1, i1)])
    
    to_return = gs1.handle_end(grid, gs1_len, gs2_len, end1, end2, gs1, gs2)
        
    return tuple(to_return)


def collect(output):
    """
    This collects all like-terms loops over the generating series in the
    output.
    """
    coefficient_count = defaultdict(int)
    term_storage = {}
    output_collected = []
    
    for gs in output:
        coefficient_count[hash(gs)] += gs.coeff
        term_storage[hash(gs)] = gs

    for term_hash, coeff in coefficient_count.items():
        temp = term_storage[term_hash]
        temp.coeff = coeff
        output_collected.append(temp)

    return output_collected


def collect_grid(terms):
    """
    
    """
    instance_counter = defaultdict(int)
    term_storage = dict()
    
    for count, term in terms:
        gs_hash = hash(term)
        instance_counter[gs_hash] += count
        if gs_hash not in term_storage:
            term_storage[gs_hash] = term
    
    collected_terms = []
    for key, term in term_storage.items():
        temp_term = (instance_counter[key], term)
        collected_terms.append(temp_term)
    
    return collected_terms

    
def wrap_term(term: Union[List, GS]) -> List:
    """
    This is used to wrap terms as some functions iterate over lists, but in
    some cases singular objects may be passed.
    """
    if isinstance(term, list):
        pass
    else:
        term = [term]
    return term
 

def partitions(iter_depth: int, number_of_shuffles: int) -> Tuple[int]:
    """
    Rather than coming up with a fancy way of generating all the partitions of
    a number, this uses the itertools' product function to calculate the
    Cartesian product, and then eliminate all the entries that don't sum to
    iter_depth. Therefore giving all the partitions.
    
    There is an edge case at iter_depth == 1, in this case all the permutations
    of 1 and padding zeros are output.
    """
    if iter_depth == 0:
        parts = [(0, ) * number_of_shuffles]
    
    elif iter_depth == 1:
        parts = list(set(permutations([0] * (number_of_shuffles - 1) + [1])))
    
    else:
        parts = product(range(iter_depth), repeat=number_of_shuffles)
        parts = [i for i in parts if sum(i) == iter_depth]
        iter_depth_with_zeros = list(
            set(permutations([0] * (number_of_shuffles - 1) + [iter_depth]))
        )
        parts.extend(iter_depth_with_zeros)
    
    return parts


@shuffle_cacher
def nShuffles(
        *args: Union[GS, List[GS]]
) -> List[GS]:
    """
    This takes variadic input, greater than 2 and outputs the shuffle product.
    """
    if len(args) < 2:
        raise ValueError("nShuffles requires two or more inputs.")
    
    # Manually calculate the shuffle product of the first two arguments.
    output_gs = []
    gs1 = wrap_term(args[0])
    gs2 = wrap_term(args[1])
    for gs1_term in gs1:
        for gs2_term in gs2:
            temp_output = binary_shuffle(gs1_term, gs2_term)
            temp_output = collect(temp_output)
            output_gs.extend(temp_output)
        output_gs = collect(output_gs)
    output_gs = collect(output_gs)
    
    # Iterate over the remaining arguments.
    for gs_i in args[2:]:
        storage = []
        for gs_j in output_gs:
            temp_output = binary_shuffle(gs_i, gs_j)
            temp_output = collect(temp_output)
            storage.extend(temp_output)
        output_gs = collect(storage)
    output_gs = collect(output_gs)
    
    return output_gs


def iter_gs_worker(part, term_storage, depth):
    """
    This is the CPU-intensive section the generating series expansion.
    """
    terms = itemgetter(*part)(term_storage)
    # Cartesian product of all the inputs, instead of nested for-loop. Same
    # thing but avoids unnecessary nesting.
    for in_perm in product(*terms):
        term_storage[depth + 1].extend(nShuffles(*in_perm))
    

def iterate_gs(g0, multipliers, n_shuffles, iter_depth=2, return_type=tuple):
    """
    This follows the iterative procedure of determining the generating series
    by summing over the shuffles of all the partitions of a number. The
    multiplier is the multiplier at the end of every interation step.
    g0 is the initial term used in the iteration. This function is only valid
    for when there is a singular shuffle product of length n. For instance
    when multiple shuffle products are required, such as in a duffing
    oscillator with a quadratic term, there are two distinct shuffle products
    required, one for the quadratic nonlinearity and one for the cubic.
    """
    multipliers = wrap_term(multipliers)
    g0 = wrap_term(g0)
    
    term_storage = defaultdict(list)
    term_storage[0].extend(g0)
    
    for depth in range(iter_depth):
        for part in partitions(depth, n_shuffles):
            iter_gs_worker(part, term_storage, depth)
        term_storage[depth + 1] = collect(term_storage[depth + 1])
        
        # After the shuffles for this iteration's depth have been caluclated,
        # prepend the multiplier to each term.
        for gs_term in term_storage[depth + 1]:
            for multiplier in multipliers:
                gs_term.prepend_multiplier(multiplier)
                    
    return g0[0].handle_output_type(term_storage, return_type)


def sdof_roots(m, c, k):
    """
    Values are passed in their usual orders, however the quadratic coefficient
    is k, therefore need to reverse the order when passed into np.roots.
    
    As a result of floating point precision, when the determinant == 0, some
    complex artefacts can be introduced, in this case, I take the real part of
    the roots.
    """
    det = c**2 - 4*k*m
    roots = np.roots([m, c, k])  # Reversed as quadratic is kx^2 + cx + m.
    if det == 0:
        roots = np.real(roots)

    return roots


def impulse_from_iter(g0, multipliers, n_shuffles, iter_depth=2, amplitude=1):
    """
    The idea here centers around the fact that most of the term in the impulse
    response are thrown away. So when iterating the generating series, the
    terms that will definitely not result in any terms later on can be thrown
    away early, therefore we no longer have to expand these terms, this results
    in a efficiency gains when comparing to expanding the generating series
    and then applying the impulse response.
    """
    x0, x1 = symbols("x0 x1")
    
    multipliers = wrap_term(multipliers)
    g0 = wrap_term(g0)
    
    term_storage = defaultdict(list)
    term_storage[0].extend(g0)
    
    for depth in range(iter_depth):
        for part in partitions(depth, n_shuffles):
            # Cartesian product of all the inputs, instead of nested for-loop.
            terms = itemgetter(*part)(term_storage)
            for in_perm in product(*terms):
                term_storage[depth + 1].extend(nShuffles(*in_perm))
            term_storage[depth + 1] = collect(term_storage[depth + 1])
        
        # After the shuffles for this iteration's depth have been caluclated,
        # prepend the multiplier to each term.
        next_terms = []
        for gs_term in term_storage[depth + 1]:
            been_1 = False
            for x in symbols("x0 x1"):
                if x == x1:
                    been_1 = True
                elif been_1 and x == x0:
                    break
            else:
                for multiplier in multipliers:
                    gs_term.prepend_multiplier(multiplier)

        term_storage[depth + 1] = next_terms
    
    tuple_form = g0[0].handle_output_type(term_storage, tuple)
    
    return impulse(tuple_form, amplitude)
