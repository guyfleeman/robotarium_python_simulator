from rps.robotarium import Robotarium
from rps.program import DrivenRobotariumProgram

from threading import Condition
from threading import Timer
import time

import numpy as np

class RobotariumDriver():
	
	def __init__(self, logger):
		# program
		self.prog = None

		# logging
		self.logger = logger

		# sim
		self.sim = None

		# sim control 
		self.sim_running = False
		self.normal_stop = True
		self.sim_notif_cond = Condition()
		self.sim_step_timer = None
		self.sim_rt_prop = None

		# sim performance metrics
		self.sim_step_ct = 0
		self.sim_start_time = 0
		self.sim_last_step_time = 0


	def set_program(self, prog):
		if not isinstance(prog, DrivenRobotariumProgram):
			raise TypeError('The given program was not an instance of DrivenRobotariumProrgam')

		self.prog = prog


	def start_simulator(self):
		# call sim_setup to allow the program to setup
		self.prog.sim_setup()

		# create the simulator
		num_agents = self.prog.get_num_agents()
		self.sim = Robotarium(number_of_agents=num_agents, \
				      save_data=False, \
				      update_time=(-1))

		self.logger.info('robotarium created')

		# create the clock driver
		self.sim_rt_prop = self.prog.get_runtime_properties()
		self.sim_step_timer = Timer(self.sim_rt_prop['interval'], 
					    self.__step_interval_governor)

		self.logger.info('calling simulation pre start...')

		# let the program do pre-start calculatons	
		self.prog.sim_pre(self.sim.get_poses())

		# start the step timer
		self.sim_start_time = time.time()
		self.logger.info('starting sim at timestamp: %s', str(self.sim_start_time))
		self.sim_step_timer.start()

		while self.sim_running:
			self.sim_notif_cond.acquire()
			self.sim_notif_cond.wait(timeout=None)
			
			self.__step_simulator()

		# close sim
		self.__close_simulator()


	def __step_interval_governor(self):
		self.sim_notif_cond.acquire()
		self.sim_notif_cond.notify_all()


	def __stop_simulator(self, normal_stop=True):
		self.sim_step_timer.cancel()
		self.sim_running = False
		self.normal_stop = normal_stop


	def __step_simulator(self):
		# timing
		sim_step_interval = self.sim_rt_prop['interval']
		current_time = time.time()
		step_delta = current_time - self.sim_last_step_time
		step_skew = step_delta / sim_step_interval

		# warn against calcualtions taking inconsistent amounts of time
		sim_time_skew_factor = 1.5
		warning_time = sim_time_skew_factor * sim_step_interval
		if current_time - self.sim_last_step_time > warning_time:
			self.logger.warning('step calculation time exceeding provided step interval')

		# update time
		self.sim_last_step_time = current_time

		# call the programs step function
		done = self.prog.sim_step(self.sim.get_poses(), step_delta, step_skew)

		# pull data and update sim vels
		robot_IDs = np.arange(self.prog.get_num_agents())
		velocities = self.prog.get_velocities()
		self.sim.set_velocities(robot_IDs, velocities)

		# step the sim
		self.sim.step()

		# program indicated final/stable state reached
		if done:
			self.__stop_simulator()


		# timeout fallbacks
		if self.sim_rt_prop['timeout']:
			if self.sim_rt_prop['type'] == 'time':
				current_time = time.time()
				timeout_interval = int(self.sim_rt_prop['timeout'])
				if current_time - self.sim_start_time > timeout_interval:
					self.__stop_simulator(normal_stop=False)
			elif self.sim_rt_prop['type'] == 'step':
				if self.set_step_ct > int(self.sim_rt_prop['timeout']):
					self.__stop_simulator(normal_stop=False)

		# update the iteration counter
		self.sim_step_ct = self.sim_step_ct + 1



	def __close_simulator(self, normal_stop=True):
		self.logger.info('steps terminated at %s', str(time.time()))

		if normal_stop:
			self.logger.info('simulation steps complete')
		else:
			self.logger.warning('simulation errored or timed out')
			self.logger.warning('simulation steps not complete')

		self.logger.info('calling simulator post run...')

		# call the post processing routine of the program
		self.prog.sim_post(self.sim.get_poses())

		# close
		self.sim.call_at_scripts_end()


