from gym import Env
from gym import spaces
import numpy as np
import traci
import os
import sys
from sumolib import checkBinary 

if 'SUMO_HOME' in os.environ:
  tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
  sys.path.append(tools)
else:
  sys.exit("please declare environment variable 'SUMO_HOME'")

LIBSUMO = "LIBSUMO_AS_TRACI" in os.environ

class SumoCustom(Env):

  CONNECTION_LABEL = 0

  def __init__(self, net_file, route_file, yellow_time=5, num_seconds=10000, use_gui=False):
    """
    action_space: open green light for 10, 20, 30 seconds
    observation: lane_1_queue, ..., lane_n_queue
    """
    self.net = net_file
    self.route = route_file
    self.yellow_time = yellow_time
    self.num_seconds = num_seconds
    self.use_gui = use_gui
    self.label = str(SumoCustom.CONNECTION_LABEL)
    SumoCustom.CONNECTION_LABEL += 1

    if LIBSUMO:
      traci.start([checkBinary("sumo"), "-n", self.net])  # Start only to retrieve traffic light information
      self.conn = traci
    else:
      traci.start([checkBinary("sumo"), "-n", self.net], label="init_connection" + self.label)
      self.conn = traci.getConnection("init_connection" + self.label)

    """ It will choose to open this phases for 10, 20, 30 seconds """
    self.time_until = 0
    self.is_yellow_phase = False
    self.action_space = spaces.Discrete(3)

    if self.use_gui:
      self._sumo_binary = checkBinary("sumo-gui")
    else:
      self._sumo_binary = checkBinary("sumo")

    self.ts_id = self.conn.trafficlight.getIDList()[0]

    """ Set Green phase """
    self.all_phases = self.conn.trafficlight.getAllProgramLogics(self.ts_id)[0].phases
    self.num_all_phases = len(self.all_phases)
    self.current_phase = 0

    """ Set lanes to retrive the halting number of each lanes """
    self.lanes = self.conn.trafficlight.getControlledLanes(self.ts_id)

    """ Set Observation space """
    self.observation_space = self.observation()
    self.conn.close()

  def step(self, action):
    """ If change to next phase, must change to yellow phase first and then switch to next phase """
    next_phase = self.all_phases[(self.current_phase + 2)% self.num_all_phases].state
    yellow_phase = self.all_phases[(self.current_phase + 1)% self.num_all_phases].state

    if self.is_yellow_phase and self.conn.simulation.getTime() < self.time_until:
      self.conn.trafficlight.setRedYellowGreenState(self.ts_id, next_phase)
      self.is_yellow_phase = False
      self.time_until += (action + 1) * 10
      self.phase = (self.phase + 1) % self.num_all_phases

    if (not self.is_yellow_phase) and self.conn.simulation.getTime() >= self.time_until:
      self.conn.trafficlight.setRedYellowGreenState(self.ts_id, yellow_phase)
      self.is_yellow_phase = True
      self.time_until += self.yellow_time

    observation = self.observation()
    reward = self.get_total_queued()
    terminated = False
    truncated = self.conn.simulation.getTime() > self.num_seconds
    info = {}

    return observation, reward, terminated, truncated, info
  
  def render(self):
    if self.render_mode == "human": return  # sumo-gui will already be rendering the frame
    elif self.render_mode == "rgb_array":
      img = self.disp.grab()
      return np.array(img)

  def reset(self):
    self.start_simulation()
    return self.observation()

  def observation(self):
    """ Return the default observation """
    """ Now only observe the halting number, can adapt in the future """
    queue = self.get_lanes_queue()
    observation = np.array(queue, dtype=np.float32)
    return observation
  
  def get_lanes_queue(self):
    """ Compute from number of halting vehicles (<0.1m/s) divided by the length of lanes"""
    lanes_queue = [self.conn.lane.getLastStepHaltingNumber(lane)/self.conn.lane.getLength(lane) for lane in self.lanes]
    return lanes_queue
  
  def get_total_queued(self) -> int:
    """ Returns the total number of vehicles halting in the intersection """
    return sum(self.conn.lane.getLastStepHaltingNumber(lane) for lane in self.lanes)
  
  def start_simulation(self):
    sumo_cmd = [
      self._sumo_binary,
      "-n",
      self.net,
      "-r",
      self.route,
    ]
    
    if self.use_gui or self.render_mode is not None:
      sumo_cmd.extend(["--start", "--quit-on-end"])

    self.conn.start(sumo_cmd)

  def close(self):
    if self.sumo is None: return

    if not LIBSUMO:
        traci.switch(self.label)
    traci.close()

    if self.disp is not None:
        self.disp.stop()
        self.disp = None

    self.sumo = None