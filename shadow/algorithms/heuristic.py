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

########################################################################

"""
This module contais code for implementing heuristic-based scheduling
algorithms. Currently, this file implements the following algorithms:

* HEFT 
* PHEFT 
"""
from random import randint
import operator

RANDMAX = 1000


#############################################################################
############################# HUERISTICS  ###################################
#############################################################################


def heft(workflow):
	"""
	Implementation of the original 1999 HEFT algorithm.

	:params wf: The workflow object to schedule
	:returns: The makespan of the resulting schedule
	"""
	upward_rank(workflow)
	workflow.sort_tasks('rank')
	makespan = insertion_policy(workflow)
	return makespan

def pheft(wf):
	"""
	Implementation of the PHEFT algorithm, which adaptst the HEFT algorithm
	using the concpet of an Optimistic Cost Table (OCT)
	"""

	oct_rank_matrix = dict()  # Necessary addition for PHEFT
	upward_oct_rank(wf, oct_rank_matrix)
	makespan = insertion_policy_oct(wf, oct_rank_matrix)
	return makespan


# TODO: Partial Critical Paths 
def pcp(wf):
	return None


# TODO: Multi-objective list scheduling
def mols(wf):
	return None


#############################################################################
############### HELPER FUNCTIONS & HEURISTIC-SPECIFIC POLICIES ##############
#############################################################################


def upward_rank(wf):
	"""
	Ranks tasks according to the specified method. Tasks need to be ranked,
	then sorted according to the rank. Returns a sorted list of tasks in
	order of rank.
	"""
	for task in sorted(list(wf.tasks)):
		rank_up(wf, task)


def upward_oct_rank(wf, oct_rank_matrix):
	for val in wf.env.machines:
		for node in sorted(list(wf.tasks()), reverse=True):
			rank_oct(wf, oct_rank_matrix, node, val)

	for task in wf.tasks:
		ave = 0
		for (t, p) in oct_rank_matrix:
			if t is task:
				ave += oct_rank_matrix[(t, p)]

		rank = int(ave / len(wf.env.machines))
		task.rank = rank


def rank_up(wf, task):
	"""
	Upward ranking heuristic outlined in Topcuoglu, Hariri & Wu (2002)
	Closely modelled off 'cal_up_rank' function at:
	https://github.com/oyld/heft/blob/master/src/heft.py

	Ranks individual tasks and then allocates this final value
	to the attribute of the workflow graph

	:param wf - Subject workflow
	:param task -  A task task in an DAG that is being ranked
	"""
	longest_rank = 0
	for successor in wf.graph.successors(task):
		if successor.rank == -1:  # if we have not assigned a rank
			rank_up(wf, successor)

		longest_rank = max(
			longest_rank, ave_comm_cost(wf, task, successor)
			+ successor.rank
		)

	task.rank = task.calc_ave_runtime() + longest_rank


def rank_up_random(wf, task):
	"""
	Computes the upward rank based on either the average, max or minimum
	computational cost
	"""

	longest_rank = 0
	for successor in wf.successors(task):
		if 'rank' not in wf.tasks[successor]:
			# if we have not assigned a rank
			rank_up(wf, successor)

		longest_rank = max(
			longest_rank, ave_comm_cost(wf, task, successor)
						+ wf.tasks[successor]['rank'])

	randval = randint(0, RANDMAX) % 3
	ave_comp = 0
	if randval is 0:
		ave_comp = ave_comp_cost(wf, task)
	elif randval is 1:
		ave_comp = max_comp_cost(wf, task)
	elif randval is 2:
		ave_comp = max_comp_cost(wf, task)

	wf.tasks[task]['rank'] = ave_comp + longest_rank


def rank_oct(wf, oct_rank_matrix, task, pk):
	"""
	Optimistic cost table ranking heuristic outlined in
	Arabnejad and Barbos (2014)
	"""
	max_successor = 0
	for successor in wf.graph.successors(task):
		min_machine = 1000
		for machine in wf.machine_alloc:
			oct_val = 0
			if (successor, machine) not in oct_rank_matrix.keys():
				rank_oct(wf, oct_rank_matrix, successor, machine)
			comm_cost = 0
			comp_cost = successor.calculated_runtime[machine]
			if machine is not pk:
				comm_cost = ave_comm_cost(wf, task, successor)
			oct_val = oct_rank_matrix[(successor, machine)] + \
					comp_cost + comm_cost
			min_machine = min(min_machine, oct_val)
		max_successor = max(max_successor, min_machine)

	oct_rank_matrix[(task, pk)] = max_successor

def ave_comm_cost(wf, task, successor):
	"""
	Returns the 'average' communication cost, which is just
	the cost in the matrix. Not sure how the ave. in the
	original paper was calculate or represented...

	:params task: Starting task
	:params successor: Node with which the starting task is communicating
	"""
	# TODO sort out data rates in future release
	# cost, zeros = 0, 0
	# data_product_size = wf.graph.edges[task, successor]['data_size']
	# for val in range(len(wf.system['data_rate'][0])):
	# 	rate = wf.system['data_rate'][0][val]
	# 	if rate != 0:
	# 		cost += data_product_size / rate
	# 	else:
	# 		zeros += 1
	# denominator = len(wf.system['data_rate'][0]) - zeros
	#
	# # if denominator is 0, the data rate between each machine is negligible.
	# if denominator == 0:
	# 	return 0
	# else:
	# 	return int(cost / denominator)

	return wf.graph.edges[task, successor]['data_size']


def ave_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return sum(comp) / len(comp)


def max_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return max(comp)


def min_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return min(comp)


def calc_est(wf, task, machine):
	"""
	Calculate the Estimated Start Time of a task on a given processor
	"""

	est = 0
	predecessors = wf.graph.predecessors(task)
	for pretask in predecessors:
		# If task isn't on the same processor, there is a transfer cost
		pre_machine = pretask.machine
		# rate = wf.system['data_rate'][pre_processor][machine]
		if pre_machine != machine:  # and rate > 0:
			comm_cost = int(wf.graph.edges[pretask, task]['data_size'])  # / rate)
		else:
			comm_cost = 0

		aft = pretask.aft
		tmp = aft + comm_cost
		if tmp >= est:
			est = tmp

	machine_str = machine
	curr_allocations = wf.solution.list_machine_allocations(machine_str)
	available_slots = []
	num_alloc = len(curr_allocations)
	prev = None
	if num_alloc == 0:
		test = 0
	else:
		for i,alloc in enumerate(curr_allocations):
			if i == 0:
				if alloc.ast !=0: # If the start time of the first allocation is not 0
					available_slots.append((0, alloc.ast))
				else:
					continue
			else:
				prev_alloc = curr_allocations[i-1]
				available_slots.append((
					prev_alloc.aft,
					alloc.ast
				))
		final_alloc = curr_allocations[num_alloc-1] # We want the finish time of the latest allocation.
		available_slots.append((final_alloc.aft, -1))

	for slot in available_slots:
		if est < slot[0] and slot[0] + \
				task.calculated_runtime[machine] <= slot[1]:
			return slot[0]
		if (est >= slot[0]) and est + task.calculated_runtime[machine] <= slot[1]:
			return est
		# At the 'end' of available slots
		if (est >= slot[0]) and (slot[1] < 0):
			return est
		# This last case occurs when we have a low est but a high cost, so
		# it doesn't fit in any gaps; hence we have to put it at the 'end'
		# and start it late
		if (est < slot[0]) and (slot[1] < 0):
			return slot[0]

	return est


def insertion_policy(wf):
	"""
	Allocate tasks to machines following the insertion based policy outline
	in Tocuoglu et al.(2002)
	"""
	makespan = 0
	# tasks = sort_tasks(wf, 'rank')
	sorted_tasks = wf.sort_tasks('rank')
	# tmp = wf.tasks
	for task in sorted_tasks:
		# Treat the first task differently, as it's the easiest to get the lowest cost
		if task == list(wf.tasks)[0]:  # Convert networkx NodeView to list
			m, w = min(
				task.calculated_runtime.items(),
				key=operator.itemgetter(1)
			)
			task.machine = m
			task.ast = 0
			task.aft = w

			wf.solution.add_allocation(task=task, machine=m)
		else:
			aft = -1  # Finish time for the current task
			m = 0
			for machine in wf.env.machines:
				# tasks in self.rank_sort are being updated, not wf.graph;
				est = calc_est(wf, task, machine)
				if aft == -1:  # assign initial value of aft for this task
					aft = est + task.calculated_runtime[machine]
					m = machine
				# see if the next processor gives us an earlier finish time
				elif est + task.calculated_runtime[machine] < aft:
					aft = est + task.calculated_runtime[machine]
					m = machine

			task.machine = m
			task.ast = aft - task.calculated_runtime[m]
			task.aft = aft

			if task.ast >= makespan:
				makespan = task.aft

			wf.solution.add_allocation(task=task, machine=m)

	wf.makespan = makespan
	wf.solution.makespan = makespan
	return makespan


def insertion_policy_oct(wf, oct_rank_matrix):
	"""
	Allocate tasks to machines following the insertion based policy outline
	in Tocuoglu et al.(2002)
	"""

	makespan = 0
	if not oct_rank_matrix:
		upward_oct_rank(wf, oct_rank_matrix)
	eft_matrix = dict()
	oeft_matrix = dict()
	m = None
	sorted_tasks = wf.sort_tasks('rank')
	for task in sorted_tasks:
		if task == list(wf.tasks)[0]:
			task.ast = 0
			min_oeft = -1
			for machine in wf.machine_alloc:
				eft_matrix[(task, machine)] = task.calculated_runtime[machine] 
				oeft_matrix[(task, machine)] = \
					eft_matrix[(task, machine)] + oct_rank_matrix[(task, machine)]
				if (min_oeft == -1) or \
						(oeft_matrix[(task, machine)] < min_oeft):
					min_oeft = oeft_matrix[(task, machine)]
					m = machine
			task.aft = task.calculated_runtime[m]
			task.machine = m
			wf.solution.add_allocation(task=task, machine=m)
		else:
			min_oeft = -1
			for machine in wf.machine_alloc:
				if wf.graph.predecessors(task):
					est = calc_est(wf, task, machine)
				else:
					est = 0
				eft = est + task.calculated_runtime[machine]
				eft_matrix[(task, machine)] = eft

				oeft_matrix[(task, machine)] = \
					eft_matrix[(task, machine)] + oct_rank_matrix[(task, machine)]
				if (min_oeft == -1) or \
						(oeft_matrix[(task, machine)] < min_oeft):
					min_oeft = oeft_matrix[(task, machine)]
					m = machine

			task.aft = eft_matrix[(task, m)]
			task.ast = task.aft - task.calculated_runtime[m]
			task.machine = m

			if task.aft >= makespan:
				makespan = task.aft
			wf.solution.add_allocation(task=task, machine=m)

	wf.solution.makespan = makespan
	return makespan


