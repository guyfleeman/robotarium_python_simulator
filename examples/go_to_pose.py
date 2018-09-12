import rps.robotarium as robotarium
from rps.program import DrivenRobotariumProgram
from rps.utilities.transformations import *
from rps.utilities.barrier_certificates import *
from rps.utilities.misc import *
from rps.utilities.controllers import *

import numpy as np

class GoToPose(DrivenRobotariumProgram):
	
	def __init__(self):
		super().__init__()
		print("Creating GoToPose")

	def sim_setup(self):
		print("Setup")

	def sim_pre(self, poses):
		print("Pre")

	def sim_step(self, poses, step_delta, step_skew):
		print("Step")

		return False

	def sim_post(self, poses):
		print("Post")

