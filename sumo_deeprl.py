import os
import sys
import traci
from sumolib import checkBinary 
import pandas as pd
from sumo_rl import SumoEnvironment
import xml.etree.ElementTree as ET
class SumoDeepRl:
  
  def __init__(self, junction_name):
    self.junction_name = junction_name
    self._net = f'{junction_name}/junction.net.xml'

    if 'SUMO_HOME' in os.environ:
      tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
      sys.path.append(tools)
    else:
      sys.exit("please declare environment variable 'SUMO_HOME'")
  
  def create_environment(self, sim_time, route_file, num_seconds=100000,reward_fn='diff-waiting-time', useGui=False, yellow_time=4):
    route_path = f"{self.junction_name}/{sim_time}/trips/{route_file}"
    return SumoEnvironment(
      net_file=self._net,
      route_file=route_path,
      single_agent=True,
      use_gui=useGui,
      num_seconds=num_seconds,
      delta_time=yellow_time+1,
      yellow_time=yellow_time,
      reward_fn=reward_fn,
      waiting_time_memory=10000,
    )
  
  def create_routes(self, route_details, time, total_cars):
    """
    Usage Example: route_details = {n: ['-E2', 6], s: ['-E0', 6], e: ['-E3', 3], w: ['-E1', 2]}
    Results save in: [junction_name]/[time]/trips/...
    """
    root = ET.Element("routes")
    output_name = str(total_cars) + '.rou.xml'

    direction = ['n', 's', 'e', 'w']
    total_weight = sum(weight[1] for weight in route_details.values())

    for dir1 in direction:
      total_dir1 = round(route_details[dir1][1]/total_weight*total_cars)
      for dir2 in direction:
        sub_weight= total_weight - route_details[dir1][1]
        total_dir2 = round(route_details[dir2][1]/sub_weight*total_dir1)
        if(dir1 != dir2):
          if(len(route_details[dir2][0]) == 3):
            edges = route_details[dir1][0] + ' ' + route_details[dir2][0][1:]
          else:
            edges = route_details[dir1][0] + ' ' + '-' + route_details[dir2][0]

          ET.SubElement(root, "route", id=f"route_{dir1}{dir2}", edges=edges)
          ET.SubElement(root, "flow", id=f"flow_{dir1}{dir2}", route=f"route_{dir1}{dir2}",
                          begin="0",end=str(time),
                          vehsPerHour=str(total_dir2),
                          departSpeed="max", departPos="base", departLane="best")
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')

    time_name = f"{str(time/3600)}hour"
    output_dir = os.path.join(self.junction_name, time_name, 'trips')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, output_name)
    tree.write(output_file)
    print('Create Success')

  def save_predict(self, vph, waiting_times, clear_simulations, trained_number_veh, reward, trained_route_time):
    """
    Save in: [junction_name]/[trained_route_time]/result.csv
    """
    folder_path = f'{self.junction_name}/{trained_route_time}'
    file_path = f'{folder_path}/result.csv'

    if not os.path.exists(folder_path):
      os.makedirs(folder_path)

    if os.path.exists(file_path):
      df = pd.read_csv(file_path)
    else:
      df = pd.DataFrame({'Vehicle Per Hour': vph})

    wait_name = f'{reward}_{trained_number_veh}_waiting_predict'
    clear_name = f'{reward}_{trained_number_veh}_clear_predict'
    df[wait_name] = waiting_times
    df[clear_name] = clear_simulations

    df.to_csv(f'{file_path}', index=False)

  def save_fixed(self, vph, waiting_times, clear_simulations, trained_route_time):
    folder_path = f'{self.junction_name}/{trained_route_time}'
    file_path = f'{folder_path}/result.csv'

    if not os.path.exists(folder_path):
      os.makedirs(folder_path)
  
    if os.path.exists(file_path):
      df = pd.read_csv(file_path)
    else:
      df = pd.DataFrame({'Vehicle Per Hour': vph})

    wait_name = 'waiting_fixed'
    clear_name = 'clear_fixed'
    df[wait_name] = waiting_times
    df[clear_name] = clear_simulations

    df.to_csv(f'{file_path}', index=False)

  def simulation(self, sim_time, route_file, useGui=False):
    if(useGui): sumoBinary = checkBinary('sumo-gui')
    else: sumoBinary = checkBinary('sumo')

    route_path = f'{self.junction_name}/{sim_time}/trips/{route_file}'
    
    sumoCmd = [sumoBinary, "-n", self._net, "-r", route_path, "--quit-on-end", "--waiting-time-memory", "10000", "--time-to-teleport", "-1"]
    traci.start(sumoCmd)

    waiting_time = {}
    while traci.simulation.getMinExpectedNumber() > 0:
      traci.simulationStep()
      vehicles = traci.vehicle.getIDList()
      for vehicle in vehicles:
        vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
        if(vehicle not in waiting_time):
          waiting_time[vehicle] = vehicle_waiting_time
        else:
          waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
      total_clear_time = traci.simulation.getTime()  
        
    total_waiting_time = sum(waiting_time[vehicle] for vehicle in waiting_time)
    traci.close()
    return total_waiting_time, total_clear_time

  def predict(self, sim_time, route_file, model, useGui=False, yellow_time=4, num_seconds=100000):
    env = self.create_environment(sim_time=sim_time, route_file=route_file, useGui=useGui, yellow_time=yellow_time, num_seconds=num_seconds)

    departin = float(sim_time[0:3])*3600
    departin = int(departin)

    obs, info = env.reset()
    done = False
    waiting_time = {}

    while not done:
      env.render()
      action, _ = model.predict(obs)
      obs, reward, terminated, truncated, info = env.step(action)
      vehicles = traci.vehicle.getIDList()
      if len(vehicles) == 0 and total_clear_time > departin: break
      for vehicle in vehicles:
        vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
        if(vehicle not in waiting_time):
          waiting_time[vehicle] = vehicle_waiting_time
        else:
          waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
      total_clear_time = traci.simulation.getTime()
      done = terminated or truncated

    total_waiting_time = sum(waiting_time[vehicle] for vehicle in waiting_time)
    env.close()
    return total_waiting_time, total_clear_time

  def analyze_fixed(self, sim_time, vphs, useGui=False):
    waiting_time = []
    clear_time = []

    for vph in vphs:
      total_waiting_time, total_clear_time = self.simulation(sim_time=sim_time, route_file=f'{vph}.rou.xml', useGui=useGui)
      waiting_time.append(total_waiting_time)
      clear_time.append(total_clear_time)
      print(f"{vph} cars: waiting time {total_waiting_time}, clear time: {total_clear_time}")
  
    self.save_fixed(vph=vphs, waiting_times=waiting_time, 
                    clear_simulations=clear_time, 
                    trained_route_time=sim_time)

  def analyze_predict(self, model, sim_time, vphs, trained_number_veh, reward='Diff Waiting Time', useGui=False, yellow_time=4, num_seconds=100000):
    waiting_time = []
    clear_time = []

    for vph in vphs:
      total_waiting_time, total_clear_time = self.predict(sim_time=sim_time, route_file=f'{vph}.rou.xml', model=model, useGui=useGui, yellow_time=yellow_time, num_seconds=num_seconds)
      waiting_time.append(total_waiting_time)
      clear_time.append(total_clear_time)
      print(f"{vph} cars: waiting time {total_waiting_time}, clear time: {total_clear_time}")

    self.save_predict(vph=vphs, waiting_times=waiting_time, 
                      clear_simulations=clear_time, 
                      trained_number_veh=trained_number_veh, 
                      reward=reward,
                      trained_route_time=sim_time)
 
