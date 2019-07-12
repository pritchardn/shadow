# Copyright (C) 2018 RW Bunney

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

# Test workflow class and functions

import unittest

from classes.workflow import Workflow


class TestWorkflowClass(unittest.TestCase):

	def test_load_attributes(self):
		wf = Workflow('final_graph_heft.json')
		# retval = wf.load_attributes('test/data/flop_rep_test.json')

		# self.assertEqual(retval, 0)
		self.assertEqual(wf.graph.node[5]['comp'][1], 28)
		self.assertEqual(wf.graph.edges[3, 7]['data_size'], 27)
