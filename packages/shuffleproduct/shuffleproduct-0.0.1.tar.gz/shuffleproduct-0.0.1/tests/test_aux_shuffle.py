# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:07:57 2023

@author: trist
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()) + r"/shuffleproduct")
import unittest

import numpy as np
from sympy import Symbol

import shuffle as shfl


class TestPartitions(unittest.TestCase):
    """
    These are referenced against Unal's paper and Lamnabhi's thesis.
    Since order doesn't matter, all lists are sorted to make comparison easier.
    Since shfl.partitions() handles iter_depth=0, 1 as edge cases and then any
    value greater than this is handled in the same way, we actually only have
    to check upto iter_depth=4, for completeness I have gone a little further.
    """
    
    def test_iterdepth0_n2(self):
        a = shfl.partitions(0, 2)
        assert a == [(0, 0)]
      
    def test_iterdepth1_n2(self):
        a = sorted(shfl.partitions(1, 2))
        assert a == sorted([(0, 1), (1, 0)])
    
    def test_iterdepth2_n2(self):
        a = sorted(shfl.partitions(2, 2))
        assert a == sorted([(1, 1), (2, 0), (0, 2)])
    
    def test_iterdepth3_n2(self):
        a = sorted(shfl.partitions(3, 2))
        assert a == sorted([(0, 3), (3, 0), (1, 2), (2, 1)])
        
    def test_iterdepth4_n2(self):
        a = sorted(shfl.partitions(4, 2))
        assert a == sorted([(0, 4), (4, 0), (1, 3), (3, 1), (2, 2)])
        
    def test_iterdepth5_n2(self):
        a = sorted(shfl.partitions(5, 2))
        assert a == sorted([(0, 5), (5, 0), (1, 4), (4, 1), (3, 2), (2, 3)])
        
    def test_iterdepth6_n2(self):
        a = sorted(shfl.partitions(6, 2))
        assert a == sorted([
            (0, 6), (6, 0), (1, 5), (5, 1), (4, 2), (2, 4), (3, 3)
        ])
    
    def test_iterdepth0_3(self):
        a = sorted(shfl.partitions(0, 3))
        assert a == sorted([(0, 0, 0)])
    
    def test_iterdepth1_3(self):
        a = sorted(shfl.partitions(1, 3))
        assert a == sorted([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
        
    def test_iterdepth2_3(self):
        a = sorted(shfl.partitions(2, 3))
        assert a == sorted([
            (2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (0, 1, 1), (1, 0, 1)
        ])

    def test_iterdepth4_3(self):
        a = sorted(shfl.partitions(3, 3))
        assert a == sorted([
            (3, 0, 0), (0, 3, 0), (0, 0, 3),
            (2, 1, 0), (2, 0, 1), (0, 2, 1), (0, 1, 2), (1, 2, 0), (1, 0, 2),
            (1, 1, 1)
        ])

    def test_sum(self):
        """
        Test that the sum equals the iter_depth and the length of each
        partition is the number of shuffles.
        """
        for iter_depth in range(10):
            for n_shuffles in range(1, 5):
                parts = shfl.partitions(iter_depth, n_shuffles)
                for part in parts:
                    assert sum(part) == iter_depth
                    assert len(part) == n_shuffles


if __name__ == "__main__":
    unittest.main()
