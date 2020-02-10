# Copyright (C) 3/2/20 RW Bunney

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


"""
shadowgen is a utility that allows us to generate different testing scripts for shadow expeiriments

shadowgen will convert, translate, and generate workflow and environemnt files
"""
import subprocess
import os
import json
import sys
import datetime
import networkx as nx
from shadowgen_config import CURR_DIR, JSON_DIR, DOTS_DIR
from generator import generate_graph_costs, generate_system_machines
import random

print(os.getcwd())

GGEN_OUTFILE = 'ggen_out'
DATAFLOW = 'dataflow-graph'
GFORMAT = 'denselu'
EAGLE_EXT = ".graph"
EAGLE_GRAPH = 'daliuge_graphs/TestAskapCont.graph'
CHANNELS = 10
CHANNEL_SUFFIX = "_channels-{0}".format(CHANNELS)
SEED = 20
MEAN = 5000
UNIFORM_RANGE = 500
MULTIPLIER = 1
CCR = 0.5


# DAX FILE TRANSLATION
# TODO

# SAMPLE WORKFLOW GENERATION USING GGEN
def dotgen(minx, maxx, increment):
	print("Using Ggen graph generating library")

	'''
	Here, we loop through the range provided on the command line
	'''
	# prob = float(args[4])
	# increment = int(args[5])

	for x in range(minx, maxx, increment):
		today_dir = datetime.date.today().strftime("%Y-%m-%d")
		dots_path = "{0}/{1}".format(DOTS_DIR, today_dir)
		if not os.path.exists(dots_path):
			os.mkdir(dots_path)
		outfile = '{0}/{1}_{2}.dot'.format(dots_path, GFORMAT, x)
		print('Generating file: {0}'.format(outfile))
		if not os.path.exists(outfile):
			subprocess.run(['ggen', '-o', '{0}'.format(outfile), DATAFLOW, GFORMAT, str(x)])


def genjson():
	for path in sorted(os.listdir(CURR_DIR)):
		if 'dot' in path:
			print('Generating json for {0}'.format(path))
			today_dir = datetime.date.today().strftime("%Y-%m-%d")
			json_path = "{0}/{1}".format(JSON_DIR, today_dir)
			generate_graph_costs('{0}/{1}'.format(CURR_DIR, path),
								'{0}/{1}.json'.format(json_path, path[:-4]),
								0.5, 5000, 500, 'giga')
			generate_system_machines(
				'{0}/{1}_sys.json'.format(json_path, path[:-4]),
				512, 'giga', [0.9375, 0.0625], [(100, 150), (400, 500)])


## DALIUGE TRANSLATION

def edit_channels(graph_name, suffix, extension):
	f = open(EAGLE_GRAPH, 'r')
	jdict = json.load(f)
	f.close()
	# TODO make this less hard-coded?
	jdict['nodeDataArray'][0]['fields'][0]['value'] = CHANNELS
	ngraph = graph_name[:-6] + suffix + extension
	f = open(ngraph, 'w')
	json.dump(jdict, f, indent=2)
	f.close()
	return ngraph


def unroll_graph(graph):
	if os.path.exists(graph):
		print(graph)

		cmd_list = ['dlg', 'unroll-and-partition', '-fv', '-L', graph]
		jgraph_path = "{0}.json".format(graph[:-6])
		with open(format(jgraph_path), 'w+') as f:
			subprocess.call(cmd_list, stdout=f)
		return jgraph_path
	else:
		print("Failure to find path {0}".format(graph))


def generate_dot_from_networkx_graph(graph, output):
	if os.path.exists(graph):
		dot_path = "{0}.dot".format(output)
		nx.drawing.nx_pydot.write_dot(graph, dot_path)
		cmd_list = ['graphviz',
					'-Tpdf',
					'{0}.dot'.format(output)]

		dot_pdf = "{0}.pdf".format(output)
		with open(dot_pdf, 'w') as f:
			subprocess.call(cmd_list, stdout=f)
			return dot_path


def daliugeimport(graph,
				  mean,
				  uniform_range,
				  multiplier,
				  ccr,
				  seed=20):
	"""
	Daliuge import will use 
	:return:
	"""
	random.seed(seed)
	if os.path.exists(graph) and (os.stat(graph).st_size != 0):

		with open(graph) as f:
			graphdict = json.load(f)

		# Storing the nodes and edges from the unrolled DALiuGE graph
		unrolled_nx = nx.DiGraph()

		for val in graphdict:
			if 'app' in val.keys():
				if val['app'] == "dlg.apps.simple.SleepApp":
					continue
			unrolled_nx.add_node(val['oid'])
			unrolled_nx.nodes[val['oid']]['nm'] = val['nm']

		for val in graphdict:
			if 'app' in val.keys():
				if val['app'] == "dlg.apps.simple.SleepApp":
					continue
			if 'outputs' in val:
				for item in val['outputs']:
					unrolled_nx.add_edge(val['oid'], item)
			elif 'consumers' in val:
				for item in val['consumers']:
					unrolled_nx.add_edge(val['oid'], item)

		for node in unrolled_nx.nodes():
			unrolled_nx.nodes[node]['label'] = str(node)

		translate = {}
		count = 0

		for node in nx.topological_sort(unrolled_nx):
			translate[node] = count
			count = count + 1

		for key, val in translate.items():
			print(str(key) + ' :' + str(val))

		translated_graph =  nx.DiGraph()
		for key in translate:
			translated_graph.add_node(translate[key])

		for edge in unrolled_nx.edges():
			translated_graph.add_edge(translate[edge[0]], translate[edge[1]])

		for node in translated_graph.nodes():
			translated_graph.nodes[node]['label'] = str(node)

		comp_min = (mean - uniform_range) * multiplier
		comp_max = (mean + uniform_range) * multiplier

		for node in translated_graph:
			rnd = int(random.uniform(comp_min, comp_max))
			translated_graph.nodes[node]['comp'] = rnd - (rnd % multiplier)

		# Generate data loads between edges and data-link transfer rates
		comm_mean = int(mean * ccr)
		comm_min = (comm_mean - (uniform_range * ccr)) * multiplier
		comm_max = (comm_mean + (uniform_range * ccr)) * multiplier
		for edge in translated_graph.edges:
			rnd = int(random.uniform(comm_min, comm_max))
			translated_graph.edges[edge]['data_size'] = rnd - (rnd % multiplier)

		jgraph = {
			"header": {
				"time": False
			},
			'graph': nx.readwrite.node_link_data(translated_graph)
		}

		save = "{0}_shadow.json".format(graph[:-5])
		with open("{0}".format(save), 'w') as jfile:
			json.dump(jgraph, jfile, indent=2)


if __name__ == '__main__':
	dotgen(10, 50, 20)
	# genjson()
	edited_graph = edit_channels(EAGLE_GRAPH, CHANNEL_SUFFIX, EAGLE_EXT)
	unrolled_graph = unroll_graph(edited_graph)
	daliugeimport(unrolled_graph, MEAN, UNIFORM_RANGE, MULTIPLIER, CCR)
