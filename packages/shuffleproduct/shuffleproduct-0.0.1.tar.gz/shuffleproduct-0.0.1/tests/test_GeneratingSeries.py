# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:31:17 2023

@author: trist
"""
import unittest
import copy

import numpy as np
import sympy as sym

import shuffle as shfl

_arr0 = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8]
])

# class TestGeneratingSeries(unittest.TestCase):
#     def test_coeffs(self):
#         _x = sym.Symbol('x')
#         try:
#             shfl.GeneratingSeries(1, _arr0)
#             shfl.GeneratingSeries(2, _arr0)
#             shfl.GeneratingSeries(3.2, _arr0)
#             shfl.GeneratingSeries(-3.2, _arr0)
#             shfl.GeneratingSeries(_x, _arr0)
#             shfl.GeneratingSeries(-_x, _arr0)
#             shfl.GeneratingSeries(-3.1*_x, _arr0)
#             shfl.GeneratingSeries(-3.1*_x**3, _arr0)
        
#         except TypeError:
#             self.fail("coeff initialisation raised TypeError unexpectedly!")
            
            
#     def test_array(self):
#         shfl.GeneratingSeries(1, np.array([[1, 2, 3, 4], [1, 2, 3, 4]]))
#         shfl.GeneratingSeries(1, np.array([[1], [1]]))
        
#         with self.assertRaises(TypeError):
#             shfl.GeneratingSeries(1, 1)

#         with self.assertRaises(ValueError):
#             shfl.GeneratingSeries(1, np.array([[1], [2], [3]]))
#             shfl.GeneratingSeries(1, np.array([[1, 2, 4]]))
#             shfl.GeneratingSeries(1, np.array([[], []]))

        
#     def test_hash(self):
#         arr1 = copy.deepcopy(_arr0[:, :])
#         arr2 = copy.deepcopy(_arr0[:, :])
#         assert (arr1 is not arr2)
        
#         a = shfl.GeneratingSeries(1, arr1)
#         b = shfl.GeneratingSeries(1, arr2)
#         assert (hash(a) == hash(b))
        
#         a[0, 0] = 2
#         assert (hash(a) != hash(b))
        
#         a[0, 0] = 1
#         assert (hash(a) == hash(b))
        
        
#     def test_len(self):
#         assert len(shfl.GeneratingSeries(1, _arr0)) == 4

    
#     def test_getitem(self):
#         a = shfl.GeneratingSeries(1, _arr0)
        
#         assert (a[0, 0] == 1)
#         assert all(a[0] == np.array([1, 2, 3, 4]))
#         assert a[-1, -1] == 8
        
        
#     def test_setitem(self):
#         a = shfl.GeneratingSeries(1, _arr0)
#         assert (a[0, 0] == 1)
        
#         a[0, 0] = 2
#         assert (a[0, 0] == 2)


#     def test_shape(self):
#         a = shfl.GeneratingSeries(1, _arr0)
#         assert (a.shape == (2, 4))


#     def test_eq(self):
#         a = shfl.GeneratingSeries(1, _arr0)
#         b = shfl.GeneratingSeries(1, _arr0)
#         assert (a == b)
        
#         with self.assertRaises(TypeError):
#             a == 1
            

# if __name__ == "__main__":
#     unittest.main()