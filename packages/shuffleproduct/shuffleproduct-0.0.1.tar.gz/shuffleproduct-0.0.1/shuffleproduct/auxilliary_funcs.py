# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 09:35:25 2025

@author: trist
"""
import matplotlib.pyplot as plt


def plot(t, y, figax=None, legend_label="y", **kwargs):
    # Plot the results
    if not figax:
        fig = plt.figure(figsize=(10, 6))
        ax = fig.gca()
        ax.set_xlim([0, 0.4])
        ax.set_xlabel('t')
        ax.set_ylabel('y')
        ax.grid(True)
    else:
        fig, ax = figax
    
    ax.plot(t, y, label=legend_label, **kwargs)
    ax.legend()

    return (fig, ax)


def to_bmatrix(term):
    """
    
    """
    coeff = str(term[0])
    term = term[1]
    
    row1 = [coeff.replace('**', '^').replace('*', '').replace('k', 'k_')]
    row2 = []
    for i, j in zip(term[0], term[1]):
        i, j = str(i), str(j)
        row1.append(i.replace('x0', 'x_0').replace('x1', 'x_1'))
        j = j.replace('a1', 'a_1').replace('a2', 'a_2').replace("*", '')
        row2.append(j)
    else:
        row2.append("0")
    
    rv = [r'\begin{bmatrix}']
    rv += ['  ' + ' & '.join(line) + r' \\' for line in (row1, row2)]
    rv += [r'\end{bmatrix}']
    
    print("\n".join(rv))


