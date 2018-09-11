from rps.robotarium import Robotarium
from threading import Condition
from threading import Timer
import time

class RobotariumDriver():
	
	def __init__(self):
		# program
		self.prog = None

		# sim
		self.sim = None

		# sim control 
		self.sim_running = False
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


	def start_simulator(self, block=False):
		# call sim_setup to allow the program to setup
		self.prog.sim_setup()

		# create the simulator
		num_agents = self.prog.get_num_agents()
		self.sim = Robotarium(number_of_agents=num_agents, \
				      save_data=False, \
				      update_time=(-1))		

		# create the clock driver
		self.sim_rt_prop = self.prog.get_runtime_properties()
		self.sim_step_timer = Timer(sim_rt_prop['interval'], __step_simulator)

		# let the program do pre-start calculatons	
		self.prog.sim_pre(self.sim.get_poses())

		# start the step timer
		self.sim_start_time = time.time()
		self.sim_step_timer.start()

		# if this function isn't blocking, start the timer and return
		if not block:
			return
	
		while(self.sim_running):
			self.sim_notif_cond.wait(timeout=None)


	def __step_simulator(self):
		# call the programs step function
		done = self.prog.sim_step(self.sim.get_poses())

		# pull data and update sim vels
		robot_IDs = np.arange(self.prog.get_num_agents())
		velocities = self.prog.get_velocities()
		self.sim.set_velocities(robot_IDs, velocities)

		# step the sim
		self.sim.step()

		# program indicated final/stable state reached
		if done:
			__close_simulator()

		# timeout fallbacks
		if self.sim_rt_prop['timeout']:
			if self.sim_rt_prop['type'] == 'time':
				current_time = time.time()
				timeout_interval = int(self.sim_rt_prop['timeout'])
				if current_time - self.sim_start_time > timeout_interval:
					__close_simulator()
			elif self.sim_rt_prop['type'] == 'step':
				if self.set_step_ct > int(self.sim_rt_prop['timeout']):
					__close_simulator()

		# update the iteration counter
		self.sim_step_ct = self.sim_step_ct + 1

		# timing
		current_time = time.time()

		# warn against calcualtions taking inconsistent amounts of time
		sim_step_interval = self.sim_rt_prop['interval']
		sim_time_skew_factor = 1.5
		warning_time = sim_time_skew_factor * sim_step_interval
		if current_time - self.sim_last_step_time > warning_time:
			print('WARNING: the program is taking a lot of time to calculating steps')
			print('WARNING: the simulator log time consistency will be affected')

		# update time
		self.sim_last_step_time = current_time


	def __close_simulator(self):
		# cancel the step timer
		self.sim_step_timer.cancel()

		# call the post processing routine of the program
		self.prog.sim_post(self.sim.get_poses())

		# clear global running flag
		self.sim_running = False

		# signal all waiting processes that the sim has finalized data and is closing
		self.sim_notif_cond.notify_all()
