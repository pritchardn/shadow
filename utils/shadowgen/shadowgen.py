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

import sys
import datetime

from shadowgen_config import CURR_DIR, JSON_DIR, DOTS_DIR
from sample_generator import generate_graph_costs, generate_system_machines

print(os.getcwd())

GGEN_OUTFILE = 'ggen_out'
DATAFLOW = 'dataflow-graph'
GFORMAT = 'denselu'


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

def daliugeimport():
	"""
	Daliuge import will use 
	:return:
	"""

if __name__ == '__main__':
	dotgen(10, 50, 20)
	genjson()
