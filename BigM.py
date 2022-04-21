# -*- coding: utf-8 -*-
"""LO_A2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nPj7-A-wUmjmdoGPIT8IIdBsCG89uBOB
"""

import numpy as np
import pandas as pd

class BigM :
  def __init__(self, optimisation_type, A, B, C, D, M = 10000) :
    self.type = optimisation_type
    self.A = A
    self.B = B
    self.C = C
    self.D = D
    self.M = M
    
    # print(self.type, self.A, self.B, self.C, self.D, self.M)
    
    self.n = self.A.shape[1]
    self.m = self. A.shape[0]
    
    if self.type == 'max' :
      self.C = [-c for c in self.C]
      self.type = 'min'
    elif self.type != 'min' :
      raise ValueError("Invalid type")
    
    self.basic_vars = []
    self.non_basic_vars = [i for i in range(self.n)]
    
    self.standarised()
    
    self.table = None

    self.solved = False
    self.Z = None
    
  def standarised(self) :
    for i in range(self.m) :
      self.n += 1
      if self.D[i, 0] == 0 : # =
        self.A = np.hstack((self.A, np.zeros((self.m, 1))))
        self.A[i, self.n - 1] = 1
        self.C = np.vstack((self.C, np.array([self.M])))
        self.basic_vars.append(self.n - 1)
      elif self.D[i, 0] == 1 : # <= or <
        self.A = np.hstack((self.A, np.zeros((self.m, 1))))
        self.A[i, self.n - 1] = 1
        self.C = np.vstack((self.C, np.array([0])))
        self.basic_vars.append(self.n - 1)
      elif self.D[i, 0] == -1 : # >= or >
        self.D[i, 0] = 1 # reversing the inequality
        self.A[i, :] *= -1
        self.N[i, 0] *= -1
        
        self.A = np.hstack((self.A, np.zeros((self.m, 1))))
        self.A[i, self.n - 1] = 1
        self.C = np.vstack((self.C, np.array([0])))
        self.basic_vars.append(self.n - 1)
      else :
        raise ValueError("Invalid value of D[0, i]")
    
    self.basic_vars = np.array(self.basic_vars)
    self.non_basic_vars = np.array(self.non_basic_vars)
    
  def solve(self) :
    
    Cb = self.C[self.basic_vars]
    Cn = self.C[self.non_basic_vars]
    Ab = self.A[:, self.basic_vars]
    An = self.A[:, self.non_basic_vars]
    
    reduced_cost = Cn.T - Cb.T @ np.linalg.inv(Ab) @ An
    
    self.table = np.hstack((self.A, self.B))
    self.table = np.vstack((self.table, np.hstack((reduced_cost, np.zeros((1, self.table.shape[1] - reduced_cost.shape[1]))))))
    
    self.z = Cb.T @ np.linalg.inv(Ab) @ self.B

    # print(self.z)

    self.table[-1, -1] = self.z

    iteration = 1

    while True :
      print("\n\n", "*" * 20, sep = "", end = " ")
      print(f"Iteration {iteration}", end = "")
      print("*" * 20)

      with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
        print("Simplex Table:\n", pd.DataFrame(self.table, [f'x_{i}' for i in self.basic_vars] + ['c'], [f'x_{i}' for i in range(self.n)] + ['b']))
    
      self.z = self.table[-1, -1]
      print("Curent Objective Cost", self.z)

      incoming_non_basic_var = self.find_incoming_non_basic_var()
      if incoming_non_basic_var is None :
        print("Objective Cost can't be improved further")
        
        break

      outgoing_basic_var = self.find_outgoing_basic_var(incoming_non_basic_var)

      print(f"Basic Variable x_{self.basic_vars[outgoing_basic_var]} going out of Basis")
      print(f"While Non-Basic Variable x_{incoming_non_basic_var} getting into Basis")

      self.table[outgoing_basic_var , :] /= self.table[outgoing_basic_var, incoming_non_basic_var]
      for i in range(self.table.shape[0]) :
        if i == outgoing_basic_var :
          continue
        self.table[i, : ] -= self.table[i, incoming_non_basic_var] * self.table[outgoing_basic_var, :]

      iteration += 1

      temp = self.basic_vars[outgoing_basic_var]
      self.basic_vars[outgoing_basic_var] = incoming_non_basic_var
      for i in range(self.non_basic_vars.shape[0]) :
        if self.non_basic_vars[i] == incoming_non_basic_var :
          self.non_basic_vars[i] = temp

    self.solved = True
  
  def find_incoming_non_basic_var(self) :
    
    ind = None
    for i in self.non_basic_vars :
      if self.table[-1, i] < 0 :
        if ind is None :
          ind = i
        elif self.table[-1, i] < self.table[-1, ind] :
          ind = i

    return ind

  def find_outgoing_basic_var(self, incoming_non_basic_var) :

    ind = None
    for i in range(self.table.shape[0] - 1) :
      a = self.table[i, incoming_non_basic_var]
      if a > 0 :
        aa = self.table[i, -1] / a
        if ind is None :
          ind = i
        elif aa < self.table[ind, -1] / self.table[ind, incoming_non_basic_var] :
          ind = i
    
    return ind

  def get_z(self) :
    if not self.solved :
      self.solve()
    return self.z

A = np.array([
              [1, 0, -1, 1, -1, 0, 0, 0, 0, 0],
              [0, 1, 1, -1, 0, -1, 0, 1, 0, 0],
              [0, 0, 0, 0, 1, 0, 1, -1, -1, 0],
              [0, 0, 0, 0, 0, 1, -1, 0, 0, -1],
              [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            ])
B = np.array([0, 0, 0, 0, 16, 13, 10, 4, 12, 14, 7, 9, 20, 7]).reshape(-1, 1)
C = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0]).reshape(-1, 1)
D = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]).reshape(-1, 1)

# A, B, C, D

method = BigM('max', A, B, C, D)
method.solve()

print()
print(f"Optimal Objective Cost is {method.get_z()}")

