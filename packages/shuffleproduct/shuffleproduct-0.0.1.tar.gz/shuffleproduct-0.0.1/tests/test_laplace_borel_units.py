# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:35:36 2023

@author: trist
"""
import os
import sys
import unittest

import sympy as sym
from sympy.functions.elementary.exponential import exp as sympyexp

sys.path.insert(0, os.path.dirname(os.getcwd()) + r"/shuffleproduct")
import responses as rsps

x = sym.Symbol('x0')
y = sym.Symbol('y')
t = sym.Symbol('t')


# Unit test cases that should only pass lb_unit()
_unit0 = 1
_unit1 = 1.1
_unit2 = sym.core.numbers.Number(2)
_unit3 = sym.core.numbers.Number(2.1)
_unit4 = sym.core.numbers.Number(1)
_unit5 = sym.core.numbers.Number(-1)
units = [_unit0, _unit1, _unit2, _unit3, _unit4, _unit5]


# Polynomial test cases that should only pass lb_polynomial()
_poly0 = x
_poly1 = 2 * x
_poly2 = 2.1 * x
_poly3 = x ** 2
_poly4 = 2 * x ** 2
_poly5 = 2.1 * x ** 2
polys = [
    _poly0, _poly1, _poly2, _poly3, _poly4, _poly5
]

_poly_t0 = t
_poly_t1 = 2 * t
_poly_t2 = 2.1 * t
_poly_t3 = t ** 2 / 2
_poly_t4 = t ** 2
_poly_t5 = (2.1 / 2) * t**2
polys_t = [
    _poly_t0, _poly_t1, _poly_t2, _poly_t3, _poly_t4, _poly_t5
]
assert (len(polys) == len(polys_t))


# Unit test cases that should only pass lb_exponential()
_exp0 = (1 - x) ** -2
_exp1 = 2 * (1 - x) ** -2
_exp2 = 2.1 * (1 - x) ** -2
_exp3 = (1 - 2 * x) ** -2
_exp4 = 2 * (1 - 2 * x) ** -2
_exp5 = 2.1 * (1 - 2 * x) ** -2
_exp6 = (1 - 2.1 * x) ** -2
_exp7 = 2 * (1 - 2.1 * x) ** -2
_exp8 = 2.1 * (1 - 2.1 * x) ** -2
_exp9 = (1 - 2.1 * x) ** -1
_exp10 = 2 * (1 - 2.1 * x) ** -1
_exp11 = 2.1 * (1 - 2.1 * x) ** -1
_exp12 = (3.2 - 2.1 * x) ** -1
_exp13 = (x - 3.2) ** -1
_exp14 = (x - 2) ** -4
_exp15 = 5j * (1 + (3+2j)*x) ** -1
_exp16 = 5j * (1 + (3+2j)*x) ** -2
_exp17 = -3/(4*(2*x + 1) ** 2)

exps = [
    _exp0, _exp1, _exp2, _exp3, _exp4, _exp5, _exp6, _exp7, _exp8, _exp9,
    _exp10, _exp11, _exp12, _exp13, _exp14, _exp15, _exp16, _exp17
]

_exp_t0 = (1 + t) * sympyexp(t)
_exp_t1 = 2 * (1 + t) * sympyexp(t)
_exp_t2 = 2.1 * (1 + t) * sympyexp(t)
_exp_t3 = (1 + 2 * t) * sympyexp(2 * t)
_exp_t4 = 2 * (1 + 2 * t) * sympyexp(2 * t)
_exp_t5 = 2.1 * (1 + 2 * t) * sympyexp(2 * t)
_exp_t6 = (1 + 2.1 * t) * sympyexp(2.1 * t)
_exp_t7 = 2 * (1 + 2.1 * t) * sympyexp(2.1 * t)
_exp_t8 = 2.1 * (1 + 2.1 * t) * sympyexp(2.1 * t)
_exp_t9 = sympyexp(2.1 * t)
_exp_t10 = 2 * sympyexp(2.1 * t)
_exp_t11 = 2.1 * sympyexp(2.1 * t)
_exp_t12 = (1 / 3.2) * sympyexp((2.1/3.2) * t)
_exp_t13 = (1 / -3.2) * sympyexp((1 / 3.2) * t)
_exp_t14 = (-2)**-4 * (1 + 3*t/2 + 3*t**2/8 + t**3/48) * sympyexp(t/2)
_exp_t15 = 5j * sympyexp(-(3+2j)*t)
_exp_t16 = 5j * (1-(3+2j)*t) * sympyexp(-(3+2j)*t)
_exp_t17 = -3/4 * (1-2*t)*sympyexp(-2*t)
exps_t = [
    _exp_t0, _exp_t1, _exp_t2, _exp_t3, _exp_t4, _exp_t5, _exp_t6, _exp_t7,
    _exp_t8, _exp_t9, _exp_t10, _exp_t11, _exp_t12, _exp_t13, _exp_t14,
    _exp_t15, _exp_t16, _exp_t17
]
assert (len(exps) == len(exps_t))


# Unit test cases that should only pass lb_cosine()
_cos0 = (1 + x**2) ** -1
_cos1 = (1 + 2 * x**2) ** -1
_cos2 = (1 + 2.1 * x**2) ** -1
_cos3 = 2 * (1 + x**2) ** -1
_cos4 = 2 * (1 + 2 * x**2) ** -1
_cos5 = 2 * (1 + 2.1 * x**2) ** -1
_cos6 = 2.1 * (1 + x**2) ** -1
_cos7 = 2.1 * (1 + 2 * x**2) ** -1
_cos8 = 2.1 * (1 + 2.1 * x**2) ** -1
_cos9 = 2.1 * (3 + x**2) ** -1
_cos10 = 2.1 * (3 + 2 * x**2) ** -1
_cos11 = 2.1 * (3 + 2.1 * x**2) ** -1
coses = [
    _cos0, _cos1, _cos2, _cos3, _cos4, _cos5, _cos6, _cos7, _cos8, _cos9,
    _cos10, _cos11
]

_cos_t0 = sym.cos(t)
_cos_t1 = sym.cos(sym.sqrt(2) * t)
_cos_t2 = sym.cos(sym.sqrt(2.1) * t)
_cos_t3 = 2 * sym.cos(t)
_cos_t4 = 2 * sym.cos(sym.sqrt(2) * t)
_cos_t5 = 2 * sym.cos(sym.sqrt(2.1) * t)
_cos_t6 = 2.1 * sym.cos(t)
_cos_t7 = 2.1 * sym.cos(sym.sqrt(2) * t)
_cos_t8 = 2.1 * sym.cos(sym.sqrt(2.1) * t)
_cos_t9 = 2.1/3 * sym.cos(sym.sqrt(1/3) * t)
_cos_t10 = 2.1/3 * sym.cos(sym.sqrt(2/3) * t)
_cos_t11 = 2.1/3 * sym.cos(sym.sqrt(2.1/3) * t)
coses_t = [
    _cos_t0, _cos_t1, _cos_t2, _cos_t3, _cos_t4, _cos_t5, _cos_t6, _cos_t7,
    _cos_t8, _cos_t9, _cos_t10, _cos_t11
]


# Test cases that should fail every check.
_faulty3 = 1 + x + x**2
_faulty4 = (1 + x + x**2) ** -2
_faulty5 = (3 + 2.1*x + 2.1*x**2) ** -2
_faulty6 = x ** 2.1

faulties = [
    _faulty3, _faulty4, _faulty5, _faulty6
]


class TestUnit(unittest.TestCase):
    def test_unit_form(self):
        """
        Checks for true positives.
        """
        for test_var in units:
            assert rsps.is_unit_form(test_var)
    
    def test_not_unit_form(self):
        """
        Checks for false negatives.
        """
        for test_var in polys:
            assert not rsps.is_unit_form(test_var)
        
        for test_var in exps:
            assert not rsps.is_unit_form(test_var)
        
        for test_var in coses:
            assert not rsps.is_unit_form(test_var)
            
        for test_var in faulties:
            assert not rsps.is_unit_form(test_var)
    
    def test_conversion(self):
        """
        Checks that the inverse transform is the same as some hand-calculated
        results.
        """
        for test_var in units:
            assert (test_var == rsps.lb_unit(test_var))
        
    
class TestPolynomial(unittest.TestCase):
    def test_poly_form(self):
        """
        Checks for true positives.
        """
        for test_var in polys:
            assert rsps.is_polynomial_form(test_var)
        
    def test_not_poly_form(self):
        """
        Check for false negatives.
        """
        for test_var in units:
            assert not rsps.is_polynomial_form(test_var)
            
        for test_var in exps:
            assert not rsps.is_polynomial_form(test_var)
        
        for test_var in coses:
            assert not rsps.is_polynomial_form(test_var)
            
        for test_var in faulties:
            assert not rsps.is_polynomial_form(test_var)
    
    def test_conversion(self):
        """
        Checks that the inverse transform is the same as some hand-calculated
        results.
        """
        for ans, test_var in zip(polys_t, polys):
            assert ans.equals(rsps.lb_polynomial(test_var))
        

class TestExponential(unittest.TestCase):
    def test_exp_form(self):
        """
        Checks for true positives.
        """
        for test_var in exps:
            assert rsps.is_exponential_form(test_var)
    
    def test_not_exp_form(self):
        """
        Checks for false negatives.
        """
        for test_var in units:
            assert not rsps.is_exponential_form(test_var)
            
        for test_var in polys:
            assert not rsps.is_exponential_form(test_var)
        
        for test_var in coses:
            assert not rsps.is_exponential_form(test_var)
            
        for test_var in faulties:
            assert not rsps.is_exponential_form(test_var)
        
    def test_conversion(self):
        """
        Checks that the inverse transform is the same as some hand-calculated
        results.
        """
        for index, (ans, test_var) in enumerate(zip(exps_t, exps)):
            
            temp_lb = rsps.lb_exponential(test_var)
            temp = ans.equals(temp_lb)
            if not temp:
                print(index, ans, test_var, temp_lb)
            assert temp


# class TestCosine(unittest.TestCase):
#     def test_cosine_form(self):
#         """
#         Checks for true positives.
#         """
#         for test_var in coses:
#             assert rsps.is_cosine_form(test_var)
    
#     def test_not_cosine_form(self):
#         """
#         Checks for false negatives.
#         """
#         for test_var in units:
#             assert not rsps.is_cosine_form(test_var)
            
#         for test_var in polys:
#             assert not rsps.is_cosine_form(test_var)
            
#         for test_var in exps:
#             assert not rsps.is_cosine_form(test_var)
        
#         for test_var in faulties:
#             assert not rsps.is_cosine_form(test_var)
            
#     def test_conversion(self):
#         """
#         Checks that the inverse transform is the same as some hand-calculated
#         results.
        
#             ** THIS IS AN ISSUE WITH SYMPY AND HAS NO EFFECT ON THE RESULT **
#         Sympy is struggling to equate sqrt(3)/3 to its decimal expansion.
#         Therefore I am evaluating both terms at 1 and asserting that it is less
#         than a threshold value.
#         """
#         for index, (ans, test_var) in enumerate(zip(coses_t, coses)):
#             ans = sym.nsimplify(ans)
#             calculated = sym.nsimplify(rsps.lb_cosine(test_var))
            
#             if index not in (9, 10):
#                 ans.equals(calculated)
#             else:
#                 diff = (ans - calculated).subs({t: 1}).evalf()
#                 print(f"\nFloating point misalignment for Cos index {index}")
#                 print(
#                     "The difference between the two terms evaluated at 1 is ",
#                     diff
#                 )
#                 assert abs(diff) < 1e-10


if __name__ == "__main__":
    unittest.main()
