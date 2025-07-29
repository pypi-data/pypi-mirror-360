# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:10:10 2023

@author: trist
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()) + "/shuffleproduct")
import unittest

import numpy as np
from sympy import Symbol

import shuffle as shfl
import responses as rsps

x0 = Symbol("x0")
x1 = Symbol("x1")


class TestArray2Fraction(unittest.TestCase):
    """
    
    """
    
    def test_big_test(self):
        """
        I had these coded up and they're no longer of use, so may as well use
        them for testing the array_to_fraction function.
        
        gs_f are the fractions given in paper 0.
        gs are the terms from the paper I coded them up in array form.
        
        Sympy is struggling to equate things that are the same again, therefore
        the assertions are checking that the difference is less than a
        very small threshold. This is done at three different test points.
        """
        # Handling the fractional form.
        gs_f =      (1+  x0)**-1 *x1
        gs_f +=   2*(1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=  -2*(1+  x0)**-1 *x0* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=  40*(1+5*x0)**-1 *x1* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f += -40*(1+3*x0)**-1 *x0* (1+5*x0)**-1 *x1* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f += -16*(1+3*x0)**-1 *x1* (1+2*x0)**-1 *x0* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=  -4*(1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x0* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f += -40*(1+  x0)**-1 *x0* (1+5*x0)**-1 *x1* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=  40*(1+  x0)**-1 *x0* (1+3*x0)**-1 *x0* (1+5*x0)**-1 *x1* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=  16*(1+  x0)**-1 *x0* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x0* (1+4*x0)**-1 *x1* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f +=   4*(1+  x0)**-1 *x0* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x0* (1+3*x0)**-1 *x1* (1+2*x0)**-1 *x1* (1+  x0)**-1 *x1
        gs_f = gs_f.make_args(gs_f)
        
        sort_key = lambda x: abs(x.subs({x0: 1, x1: 2}))
        gs_f = sorted(gs_f, key=sort_key)
        
        # Handling the array form.
        gs = __import__("test_EquivalenceGS").TestPaperImp.gs_unsorted
        gs = gs[0].handle_output_type({0: gs}, return_type=tuple)
        
        # Converting to fractional form and sorting.
        gs_a2f = rsps.to_fraction(gs)
        gs_a2f = sorted(gs_a2f, key=sort_key)
        
        vals2 = lambda x: x.subs({x0: 2, x1: 3})
        vals3 = lambda x: x.subs({x0: 4, x1: 5})
        threshold = 1e-10
        for i, j in zip(gs_f, gs_a2f):
            assert abs(sort_key(i) - sort_key(j)) < threshold
            assert abs(vals2(i) - vals2(j)) < threshold
            assert abs(vals3(i) - vals3(j)) < threshold
                
               
if __name__ == "__main__":
    unittest.main()
