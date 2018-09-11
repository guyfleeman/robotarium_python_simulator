import rps.robotarium as robotarium
from rps.program import DrivenRobotariumProgram
from rps.utilities.transformations import *
from rps.utilities.barrier_certificates import *
from rps.utilities.misc import *
from rps.utilities.controllers import *

import numpy as np

class GoToPose(DrivenRobotariumProgram):
	
	def __init__(self):

		print("Creating GoToPose")

	def sim_setup(self):
		print("Setup")

	def sim_pre(self, poses):
		print("Pre")

	def sim_step(self, poses):
		print("Step")

		return True

	def sim_post(self, poses):
		print("Post")

