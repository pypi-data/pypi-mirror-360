# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:18:53 2023

@author: trist
"""

import os
import sys
import unittest

from sympy import Symbol
from sympy.functions.elementary.exponential import exp
import numpy as np

sys.path.insert(0, os.path.dirname(os.getcwd()) + "/shuffleproduct")
import shuffle as shfl
import responses as rsps

x0 = 0
x1 = 1
x0_s = Symbol("x0")

t = Symbol("t")


class TestImpulse(unittest.TestCase):
    """
    Compares the impulse response to the one obtained in "Functional Analysis
    of Nonlinear Circuits- A Generating Power Series Approach" - M. Lamnabhi.
    The impulse response of the system is shown in (EQ 22).
    """
    # Importing class variables from another test script.
    multipliers = __import__("test_EquivalenceGS").TestPaperImp.multipliers
    g0 = __import__("test_EquivalenceGS").TestPaperImp.g0
    iter_args = __import__("test_EquivalenceGS").TestPaperImp.iter_args
    
    # imp_frac is the impulse response from their paper in fractional form.
    imp_frac =   1.0/ (1+  x0_s)
    imp_frac +=  1/3/ (1+3*x0_s)
    imp_frac += -1/3/ (1+  x0_s) *x0_s/ (1+3*x0_s)
    imp_frac +=  1/3/ (1+5*x0_s)
    imp_frac += -1/3/ (1+3*x0_s) *x0_s/ (1+5*x0_s)
    imp_frac += -1/3/ (1+  x0_s) *x0_s/ (1+5*x0_s)
    imp_frac +=  1/3/ (1+  x0_s) *x0_s/ (1+3*x0_s) *x0_s/ (1+5*x0_s)
    # Convert to a list of terms, rather than an addition.
    imp_frac = imp_frac.make_args(imp_frac)
    
    # Sort the terms so they can reliably equated.
    def sort_key(x):
        return (abs(x.subs({x0_s: 1})), abs(x.subs({x0_s: 2})))
    
    imp_frac = sorted(imp_frac, key=sort_key)

    def test_from_their_gs_frac(self):
        """
        I've manually typed up their generating series expansion for another
        test so let's import the verified answers over and compare them to
        ensure it is not my iterative procedure for the generating series that
        is the issue. This compares against the fractional form in the class
        variable gs_frac
        """
        # Import GS terms from another test's class variable.
        correct_gs = __import__("test_EquivalenceGS").TestPaperImp.correct_gs
        correct_gs = correct_gs[0].handle_output_type(
            {0: correct_gs}, return_type=tuple
        )
        global imp_rep
        imp_rep = rsps.impulse(correct_gs)
        imp_rep = sorted(imp_rep, key=TestImpulse.sort_key)
        
        for actual, mine in zip(TestImpulse.imp_frac, imp_rep):
            try:
                assert actual.equals(mine)
            except AssertionError:
                print(actual)
                print(mine)
                print()
            
                raise AssertionError
            
    def test_from_first_principles(self):
        """
        This is testing from the system equation, therefore the iterative
        scheme for the generating series is being evaluated and then impulse
        response is determined.
        """
        scheme = shfl.iterate_gs(*TestImpulse.iter_args, iter_depth=2)
        imp_rep = rsps.impulse(scheme)
        imp_rep = sorted(imp_rep, key=TestImpulse.sort_key)
        
        for actual, mine in zip(TestImpulse.imp_frac, imp_rep):
            assert actual.equals(mine)
           
        
if __name__ == "__main__":
    unittest.main()
