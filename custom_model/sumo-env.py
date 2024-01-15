from gym import Env
from gym import spaces
import numpy as np
import traci

class SumoCustom(Env):
  def __init__(self, net_file, route_file):
    """
    Basic:
      action_space: open green light for 10, 20, 30 seconds
      observation: current_phase, lane_1_density, ..., lane_n_density
      state: 
    """
    self.net = net_file
    self.route = route_file
    self.phase = []

    pass
  def step(self):
    # get all phases 
    """
    all_phases = traci.trafficlight.getAllProgramLogics('J0')[0].phases

    if traci.simulation.getTime() % 10 == 0:
      print(traci.trafficlight.getRedYellowGreenState('J0'))
      traci.trafficlight.setRedYellowGreenState('J0', all_phases[(phase % 8)].state)
      phase += 1
    """
    pass
  def render(self):
    pass
  def reset(self):
    pass
