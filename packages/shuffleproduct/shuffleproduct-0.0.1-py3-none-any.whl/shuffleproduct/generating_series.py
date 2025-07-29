# -*- coding: utf-8 -*-
"""
Created on Fri May 12 07:57:47 2023

@author: trist
"""
import copy
from collections import deque

import numpy as np
from sympy import symbols
      

class GeneratingSeries:
    __slots__ = ("coeff", "words", "dens")
    
    def __init__(self, *args):
        if len(args) == 1:
            """
            When passing in generating series in array form.
            """
            self.coeff = np.real(args[0][0][0])
            self.words = deque(np.real(args[0][0][1:]))
            self.dens = deque(args[0][1][:-1])
        
        elif len(args) == 3:
            """
            Better form
            """
            self.coeff = args[0]
            self.words = deque(args[1])
            self.dens = deque(args[2])
                
        elif len(args) == 2:
            self.coeff = args[0]
            self.words = deque(args[1])
            self.dens = deque()
    
    @property
    def n_excites(self):
        count = 0
        x1 = symbols("x1")
        for word in self.words:
            if word == x1:
                count += 1
        return count
    
    def __repr__(self):
        """
        Makes use of sympy's printing should be implemented.
        """
        return self.__str__()

    def __hash__(self):
        """
        Hash of all the terms except for the coefficient.
        """
        return hash(tuple(self.words)) + hash(tuple(self.dens))
    
    def __eq__(self, other_obj):
        return hash(self) == hash(other_obj)
    
    def __getitem__(self, index):
        if len(self) in (index+1, 1):
            return (self.words[-1],  0)
        else:
            return (self.words[index], self.dens[index+1])
            
    def __len__(self):
        return len(self.words)
    
    def __str__(self):
        if len(self.dens) == len(self.words):
            return str(np.array([[self.coeff, *self.words], [*self.dens, 0]]))
        else:
            return f"coeff:{self.coeff}\nwords:{self.words}\ndens:{self.dens}"
    
    def scale_coeff(self, scale):
        self.coeff *= scale
        
    def prepend_multiplier(self, multiplier):
        """
        Rather than doing in place, I return here as I'm pretty sure doing it
        in place screws around with the referecing and hashes,
        
        probably doesn't have to be copy.deepcopy and the casting to float on
        the coeff could be an issue.
        """
        if isinstance(multiplier, GeneratingSeries):
            self.coeff *= multiplier.coeff
            self.words.extendleft(multiplier.words)
            self.dens.extendleft(multiplier.dens)
            
        else:
            raise TypeError("Unknown multiplier type")
           
    def get_array_form(self):
        numer = [self.coeff] + list(self.words)
        denom = list(self.den) + [0]
        
        return np.array([numer, denom])
    
    def get_term(self, index):
        return self[len(self)-index-1]
    
    def first_term(self, gs_reduct):
        return (1, GeneratingSeries(1, [gs_reduct[0]]))
    
    def reduction_term(self, g_reduce, *g_others):
        """
        Gets the term to append to the stack when reducing g1.
        """
        den_reduction = g_reduce[1]
        for g_other in g_others:
            den_reduction += g_other[1]
            
        return (g_reduce[0], den_reduction)
    
    def add_to_stack(self, grid_sec, count, new_term, current_stack):
        """
        appends the term to the stack and places it in then calls the function
        to collect the grid
        """
        current_stack = copy.deepcopy(current_stack)
        current_stack.words.appendleft(new_term[0])
        current_stack.dens.appendleft(new_term[1])
        
        grid_sec.append((count, current_stack))
        
    def get_end(self, gs):
        return (None, gs.dens[0]), gs, len(gs)
    
    def handle_end(self, grid, gs1_len, gs2_len, end1, end2, gs1, gs2):
        to_return = []
        for count, term in grid[(gs2_len, gs1_len)]:
            term.coeff *= count * gs1.coeff * gs2.coeff
            term.dens.appendleft(gs1.dens[0] + gs2.dens[0])
            to_return.append(term)
            
        return to_return
    
    def handle_output_type(self, term_storage, return_type):
        """
        Three output forms are given. The dictionary output gives the most
        stucture, where the keys represent generating series terms specific to
        an iteration depth. The list output simply returns a list of all the
        generating series, whilst they do appear in order, nothing breaks the
        order apart (unlike the dictionary). The tuple output is the form
        required for converting the generating series into the time domain. A
        function in the responses module converts the generating series array
        form into a fractional form.
        """
        if return_type == dict:
            return dict(term_storage)
        
        list_form = [i for gs in term_storage.values() for i in gs]
        if return_type == list:
            return list_form
        
        elif return_type == tuple:
            # Unpack all the gs terms into a list
            tuple_form = []
            for gs in list_form:
                tuple_form.append(
                    (gs.coeff, np.array([gs.words, gs.dens]))
                )
            return tuple_form
        
        else:
            raise TypeError("Invalid return type.")
    
    def to_array(self):
        return np.array([self.coeff, *self.words], [*self.dens, 0])

