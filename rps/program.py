from abc import ABC, abstractmethod

default_rt_properties = {
	'interval': (1.0 / 60.0),
	
	'timeout': None,
	'type': 'time'
}

class DrivenRobotariumProgram(ABC):
	def __init__(self):
		# set number of agents
		self.num_agents = 0
		
		# establish runtime
		self.rt_prop = default_rt_properties

	# sets the number of agents to be used
	def set_num_agents(self, num_agents):
		self.num_agents = num_agents


	# gets the current number of allocated agents
	def get_num_agents(self, num_agents):
		return self.num_agents

	
	def set_runtime_properties(self, rt_prop=None):
		self.rt_prop = rt_prop

	
	def get_runtime_properties(self):
		return self.rt_prop


	def set_velocities(self, velocities, robot_IDs=None):
		if robot_IDs == None:
			robot_IDs = np.arange(self.get_num_agents())

		self.velocities = velocities


	def get_velocities(self):
		return self.velocities


	@abstractmethod	
	def sim_setup(self):
		pass


	@abstractmethod
	def sim_pre(self, poses):
		pass


	@abstractmethod
	def sim_step(self, poses):
		pass


	@abstractmethod
	def sim_post(self, poses):
		pass


