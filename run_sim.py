#!/usr/bin/env python3

import argparse
import logging
import os
import pdb
import sys

def select_pyplot_renderer():
	try:
		from PyQt5 import QtCore, QtGui, QtWidgets
		import matplotlib
		matplotlib.use('Qt5Agg')
	except ImportError:
		if sys.platform == "linux" or sys.platform == "linux2":
			print('*** could not set sim renderer to Qt5Agg')
			print('*** canvas may fail to yield interactive control on close')
			print('*** please install PyQt5 if you experience issues')
			print('\tDebian Package: python3-pyqt5')
			print('\tFedora Core: python3-qt5')
			print('')
			print('*** THIS ERORR IS NOT FATAL')
			print('')

		# fallback renderer
		import matplotlib
		matplotlib.use('TkAgg')
	

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--driving', '-d',
			    action='store_true',
			    dest='sim_driving_program',
			    help='the sim steps the program: drives a DrivenRobotariumProgram')
	parser.add_argument('--log-level', '-l',
			    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
			    default='INFO',
			    dest='loglevel',
			    help='sets the log level')
	parser.add_argument('program_file',
			    nargs=1,
			    type=str,
                            metavar='program_file',
                      	    help='the Robotarium program to be run')
	return parser.parse_args()


def create_logger(loglevel):
	logger = logging.getLogger(__name__)

	numeric_level = getattr(logging, loglevel.upper(), None)
	logger.setLevel(numeric_level)

	ch = logging.StreamHandler()
	ch.setLevel(numeric_level)

	fmt='[%(asctime)s.%(msecs)01d][%(levelname)s][%(filename)s-%(funcName)s(%(lineno)s)]: %(message)s'
	date_fmt='%H:%M:%S'
	ch_fmt = logging.Formatter(fmt, date_fmt)
	ch.setFormatter(ch_fmt)

	logger.addHandler(ch)

	logger.info('created logger')
	return logger


def launch_driving_program(args):
	print('launching ' + args.program_file[0])
	os.system('python3 ' + args.program_file[0])
	print('exiting')
	exit(0)


def launch_driven_program(args):
	from rps.robotarium_driver import RobotariumDriver
	from rps.program import DrivenRobotariumProgram
	from rps.program_loader import ProgramLoader

	logger = create_logger(args.loglevel)

	logger.info('loading program...')
	prog_path = args.program_file[0]
	pl = ProgramLoader(logger)
	load_status = pl.load_module(prog_path)
	if not load_status:
		logger.critical('failed to load program module')
		exit(1)

	program_data = pl.get_program_candidates(required_ancestor=DrivenRobotariumProgram)
	if program_data == []:
		logger.critical('failed to load a valid program')
		exit(1)

	program_name = program_data[0][0]
	logger.info('loaded program: %s', program_name)
	logger.info('initializing program...')
	program_instance = program_data[0][1]()
	program_instance.set_logger(logger)
	logger.info('program initialized')
	
	logger.info('starting simulator...')
	sim_driver = RobotariumDriver(logger)
	sim_driver.set_program(program_instance)
	sim_driver.start_simulator()

	logger.info('exiting')
	exit(0)


def main():
	select_pyplot_renderer()

	args = parse_args()
	print('')
	print('Welcome to the Robotarium simulator!')
	print('')

	if (args.sim_driving_program):
		launch_driven_program(args)
	else:
		launch_driving_program(args)


# start
main()

