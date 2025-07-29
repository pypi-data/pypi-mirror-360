# -*- coding: utf-8 -*-
"""
Created on Tue May 2 17:16:23 2023

@author: trist

This serves as a check from the system equation to the time domain response.
The results are compared to previously evaluated systems in the literature.
"""
import os
import sys
import unittest

import numpy as np
from sympy import Symbol, nsimplify
from sympy.functions.elementary.exponential import exp

sys.path.insert(0, os.path.dirname(os.getcwd()) + r"/shuffleproduct")
from generating_series import GeneratingSeries
import shuffle as shfl
import responses as rsps

x0 = 0
x1 = 1
a = 2
b = 3
t = Symbol('t')


class TestPaper0(unittest.TestCase):
    """
    Compares the response to paper 0 in the papers directory. "Functional
    analysis of nonlinear circuits: a generating power series approach" -
    M.Lamnabhi.
    
    Note there is a typo in the paper, the third order 5 term should read:
    -0.041666 * exp(-t), and not 0.416666 * exp(-t).
    """
    # Import class variables from another test.
    multipliers = __import__("test_EquivalenceGS").TestPaperImp.multipliers
    g0 = __import__("test_EquivalenceGS").TestPaperImp.g0
    iter_args = __import__("test_EquivalenceGS").TestPaperImp.iter_args
    
    imp_time = exp(-t)                                        # Order 1
    imp_time += 1/2*exp(-3*t) - 1/6*exp(-t)                   # Order 3
    imp_time += 5/8*exp(-5*t) - 1/4*exp(-3*t) - 1/24*exp(-t)  # Order 5
    
    def test_impulse_response(self):
        scheme = shfl.iterate_gs(*TestPaper0.iter_args, iter_depth=2)
        imp = rsps.impulse(scheme)
        imp_partfrac = rsps.matlab_partfrac(imp)
        imp_t = rsps.inverse_lb(imp_partfrac)
        
        # Sympy is struggling to equate the decimal and fractional
        # representations, therefore use nsimplify
        assert nsimplify(imp_t).equals(nsimplify(TestPaper0.imp_time))
        

class TestPaper4(unittest.TestCase):
    """
    Compares the responses obtained to paper 4 in the papers directory.
    "Algebraic Computation of the Solutions of Some Nonlinear Differential
    Equations" - F.Lamnabhi-Lagarrigue.
    """
    multiplier = np.array([
        [-b, x0],
        [ a,  0]
    ])
    
    g0 = GeneratingSeries(np.array([
        [ 1, x1],
        [ a,  0]
    ]))
    
    iter_args = (g0, multiplier, 2)
    
    t0 = (1/a)*(1 - exp(-a*t))
    t1 = -(b/a**3) * (1 - 2*a*t*exp(-a*t) - exp(-2*a*t))

    def test_step_input(self):
        all_gs = shfl.iterate_gs(*TestPaper4.iter_args, 1)
        step_gs = rsps.step_input(all_gs)
        step_gs_partfrac = rsps.matlab_partfrac(step_gs)
        time_domain = rsps.inverse_lb(step_gs_partfrac)
        assert time_domain.equals(TestPaper4.t0 + TestPaper4.t1)


class TestPaper5(unittest.TestCase):
    """
    Compares the responses obtained to paper 4 in the papers directory.
    "Algebraic Computation of the Statistics of the Solution of Some
    Stochastic Differential Equations" - F.Lamnabhi-Lagarrigue.
    """
    multiplier = TestPaper4.multiplier
    g0 = TestPaper4.g0
    iter_args = TestPaper4.iter_args
    
    def test_gwn(self):
        print("Not Implemented gwn test.")
        pass
  
      
if __name__ == "__main__":
    unittest.main()
