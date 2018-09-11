#!/usr/bin/env python3

from rps.robotarium_driver import RobotariumDriver
from rps.program import DrivenRobotariumProgram
from rps.program_loader import ProgramLoader

import pdb
import sys

def main():
	print('Starting the Robotarium Simulator!')
	sim_diver = RobotariumDriver()

	print('Loading program')
	prog_path = sys.argv[1]
	pl = ProgramLoader(prog_path)
	program_class = pl.load(required_ancestor=DrivenRobotariumProgram)
	prog = program_class[0][1]()
	prog.set_num_agents(5)
	print(prog.get_num_agents(5))

	print('loaded program')	


# start
main()

