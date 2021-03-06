#!/usr/bin/env

# Copyright (C) 2017,2018  RW Bunney

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.  
# Temporary test runner whilst HEFT issues are ironed out from depricated
# project located at www.github.com/myxie/heft


import unittest
# import networkx as nx
# from csv import reader

# import sys
# sys.path.append('../')

from shadow.algorithms.heft import Heft


# from algorithms.utils import read_matrix


class TestHeftMethodsTopcuoglu(unittest.TestCase):
	"""
	This class test HEFT on the same example graph presented by
	Topcuoglu et al
	"""

	def setUp(self):
		self.heft = Heft('test/data/topcuoglu_comp.txt', \
						 'test/data/topcuoglu_comm.txt', \
						 'test/data/topcuoglu.graphml')

	def tearDown(self):
		return -1

	def test_rank(self):
		rank_values = [108, 77, 79, 80, 69, 63, 42, 35, 44, 14]

		self.heft.rank('up')
		sorted_nodes = self.heft.rank_sort
		for count, node in enumerate(sorted_nodes):
			# self.assertTrue(int(node.rank) == rank_values[node.tid])
			print(int(self.heft.graph.nodes[node]['rank']), rank_values[node])
			self.assertTrue(int(self.heft.graph.nodes[node]['rank']) == rank_values[node])

	def test_schedule(self):
		self.heft.rank('up')
		retval = self.heft.schedule('insertion')
		print("Makespan is: ", retval)
		self.assertTrue(retval == 80)


# @unittest.skip( 'Smaller test case')
class TestHeftMethodsOCT(unittest.TestCase):
	"""
	This class test HEFT on the same example graph presented by Arabnejad
	and Barbos
	"""

	def setUp(self):
		self.heft = Heft('test/data/oct_comp.txt', \
						 'test/data/oct_comm.txt', \
						 'test/data/oct.graphml')
		self.oct_rank_values = [72, 41, 37, 43, 31, 41, 17, 20, 16, 0]
		self.up_rank_values = [169, 114, 102, 110, 129, 119, 52, 92, 42, 20]

	def tearDown(self):
		return -1

	def test_up_rank(self):
		self.heft.rank('up')
		sorted_nodes = self.heft.rank_sort
		for count, node in enumerate(sorted_nodes):
			print(self.heft.graph.nodes[node]['rank'], \
				  self.up_rank_values[node])
			self.assertTrue(int(self.heft.graph.nodes[node]['rank']) == \
							self.up_rank_values[node])

	def test_oct_rank(self):
		self.heft.rank('oct')
		sorted_nodes = self.heft.rank_sort
		for count, node in enumerate(sorted_nodes):
			self.assertTrue(int(self.heft.graph.nodes[node]['rank']) == \
							self.oct_rank_values[node])

	@unittest.skip('Unnecessary')
	def test_oct_matrix(self):
		self.heft.rank('oct')
		for key in self.heft.oct_rank_matrix:
			print(key, self.heft.oct_rank_matrix[key])

	def test_heft_schedule(self):
		self.heft.rank('up')
		retval = self.heft.schedule('insertion')
		self.assertTrue(retval == 133)

	def test_oct_schedule(self):
		self.heft.rank('oct')
		retval = self.heft.schedule('oct_schedule')
		print('this is oct: ', retval)
		self.assertTrue(retval == 122)
