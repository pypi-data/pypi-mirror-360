# -*- coding: utf-8 -*-
"""
Created on Wed May  3 11:15:51 2023

@author: trist

WARNING: This will take along time to run because all of the calls to
rsps.matlab_partfrac() (about 80 secs).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()) + "/shuffleproduct")

import unittest

import numpy as np
from sympy import Symbol, simplify
from sympy.functions.elementary.exponential import exp

import responses as rsps
from generating_series import GeneratingSeries

# I've set these to be coprime to avoid potential factoring later on.
a = 2
b = 3

x0 = 0
x1 = 1

x0_sym = Symbol("x0")
x1_sym = Symbol("x1")
t = Symbol('t')


class TestPaper0(unittest.TestCase):
    """
    Equivalence tests against the terms obtained in paper 0 in the papers
    directory.
    
    Note there is a typo in the paper, the third order 5 term should read:
    -0.041666 * exp(-t), and not 0.416666 * exp(-t).
    """
    gs = __import__("test_EquivalenceGS").TestPaperImp.gs_unsorted
    gs = gs[0].handle_output_type({0: gs}, return_type=tuple)
    
    imp_time = exp(-t)                                        # Order 1
    imp_time += 1/2*exp(-3*t) - 1/6*exp(-t)                   # Order 3
    imp_time += 5/8*exp(-5*t) + 1/4*exp(-3*t) - 1/24*exp(-t)  # Order 5
    
    # Testing that the impulse function gives the correct response for each
    # term.
    def test_term0_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[0]])[0]
        actual = 1 / (1 + x0_sym)
        assert actual.equals(calculated)
        
    def test_term1_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[1]])[0]
        actual = 1/3 / (1 + 3*x0_sym)
        assert actual.equals(calculated)
        
    def test_term2_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[2]])[0]
        actual = -1/3 / (1+x0_sym) * x0_sym / (1+3*x0_sym)
        assert actual.equals(calculated)
        
    def test_term3_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[3]])[0]
        actual = 1/3 / (1 + 5*x0_sym)
        assert actual.equals(calculated)
              
    def test_term4_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[4]])[0]
        actual = -1/3 / (1+3*x0_sym) * x0_sym / (1+5*x0_sym)
        assert actual.equals(calculated)
        
    def test_term5_imp(self):
        assert not rsps.impulse([TestPaper0.gs[5]])
        
    def test_term6_imp(self):
        assert not rsps.impulse([TestPaper0.gs[6]])
   
    def test_term7_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[7]])[0]
        actual = -1/3/(1+x0_sym) * x0_sym/(1+5*x0_sym)
        assert actual.equals(calculated)
    
    def test_term8_imp(self):
        calculated = rsps.impulse([TestPaper0.gs[8]])[0]
        actual = 1/3/(1+x0_sym) * x0_sym/(1+3*x0_sym) * x0_sym/(1+5*x0_sym)
        assert actual.equals(calculated)
        
    def test_term9_imp(self):
        assert not rsps.impulse([TestPaper0.gs[9]])

    def test_term10_imp(self):
        assert not rsps.impulse([TestPaper0.gs[10]])
    
    # Testing the inverse laplace borel transform for each of the nonzero
    # terms.
    def test_term0_lb(self):  # Order 1
        imp = rsps.impulse([TestPaper0.gs[0]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = exp(-t)
        assert actual.equals(time)
        
    def test_term1_lb(self):  # Order 3
        imp = rsps.impulse([TestPaper0.gs[1]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/3 * exp(-3*t)
        assert actual.equals(time)
    
    def test_term2_lb(self):   # Order 3
        imp = rsps.impulse([TestPaper0.gs[2]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/6 * (exp(-3*t) - exp(-t))
        assert actual.equals(time)
    
    def test_term3_lb(self):   # Order 5
        imp = rsps.impulse([TestPaper0.gs[3]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/3 * exp(-5*t)
        assert actual.equals(time)
        
    def test_term4_lb(self):  # Order 5
        imp = rsps.impulse([TestPaper0.gs[4]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/6 * (exp(-5*t) - exp(-3*t))
        assert actual.equals(time)

    def test_term7_lb(self):  # Order 5
        imp = rsps.impulse([TestPaper0.gs[7]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/12 * (exp(-5*t) - exp(-t))
        assert actual.equals(time)
        
    def test_term8_lb(self):  # Order 5
        imp = rsps.impulse([TestPaper0.gs[8]])
        imp_pf = rsps.matlab_partfrac(imp)
        time = rsps.inverse_lb(imp_pf)
        actual = 1/24 * (exp(-5*t)-2*exp(-3*t) + exp(-t))
        assert actual.equals(time)
    
        
class TestPaper4(unittest.TestCase):
    """
    Equivalence tests against the terms obtained in paper 4. This deals with
    the conversion to the time domain section of the problem.
    """
    
    g0 = (1, GeneratingSeries(
        [[x1],
         [ a]]
    ))
    g1 = (-2*b, GeneratingSeries(
        [[x0,  x1, x1],
         [ a, 2*a,  a]]
    ))
    g2 = (4*b**2, GeneratingSeries(
        [[x0,  x1, x0,  x1, x1],
         [a, 2*a,  a, 2*a,  a]]
    ))
    
    def test_term1_arr2frac(self):
        calculated = rsps.to_fraction([TestPaper4.g0])[0]
        actual = x1_sym / (1 + a*x0_sym)
        assert calculated.equals(actual)

    def test_term1_step(self):
        g0 = rsps.step_input([TestPaper4.g0])
        calculated = rsps.matlab_partfrac(g0)[0]
        actual = 1/a - 1/(a + a**2*x0_sym)
        assert calculated.equals(actual)

    def test_term1_lb(self):
        part_fracs = 1/a - 1/(a + a**2*x0_sym)
        calculated = rsps.inverse_lb([part_fracs])
        actual = (1/a)*(1 - exp(-a*t))
        assert calculated.equals(actual)
    
    def test_term2_arr2frac(self):
        test = rsps.to_fraction([TestPaper4.g1])[0]
        numerator = -2*b * x0_sym*x1_sym**2
        denominator = (1+a*x0_sym)**2 * (1+2*a*x0_sym)
        assert test.equals(numerator / denominator)
    
    def test_term2_step(self):
        g1 = rsps.step_input([TestPaper4.g1])
        calculated = rsps.matlab_partfrac(g1)[0]
        actual = (2*b)/(a**3*(a*x0_sym + 1))
        actual -= b/a**3 + (2*b)/(a**3*(a*x0_sym + 1)**2)
        actual += b/(a**3*(2*a*x0_sym + 1))
        assert calculated.equals(actual)
        
    def test_term2_lb(self):
        part_fracs = (2*b)/(a**3*(a*x0_sym + 1))
        part_fracs -= b/a**3 + (2*b)/(a**3*(a*x0_sym + 1)**2)
        part_fracs += b/(a**3*(2*a*x0_sym + 1))
        calculated = rsps.inverse_lb([part_fracs])
        actual = -b/a**3 * (1 - 2*a*t*exp(-a*t) - exp(-2*a*t))
        assert calculated.equals(actual)
        
    def test_term3_arr2frac(self):
        test = rsps.to_fraction([TestPaper4.g2])[0]
        test = simplify(test)
        numerator = 4*b**2 * x0_sym**2 * x1_sym**3
        denominator = (1 + a*x0_sym)**3 * (1 + 2*a*x0_sym)**2
        term = simplify(numerator / denominator)
        assert term.equals(numerator / denominator)

  
if __name__ == "__main__":
    unittest.main()