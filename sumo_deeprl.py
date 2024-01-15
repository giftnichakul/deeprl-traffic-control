import os
import sys
import traci
from sumolib import checkBinary 
import pandas as pd
from sumo_rl import SumoEnvironment
import xml.etree.ElementTree as ET

class SumoDeepRl:
  
  def __init__(self, net_file):
    self._net = net_file

    if 'SUMO_HOME' in os.environ:
      tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
      sys.path.append(tools)
    else:
      sys.exit("please declare environment variable 'SUMO_HOME'")
  
  def create_environment(self, route_file, useGui=False, yellow_time=4):
    return SumoEnvironment(
      net_file=self._net,
      route_file=route_file,
      single_agent=True,
      use_gui=useGui,
      delta_time=yellow_time+1,
      yellow_time=yellow_time,
    )
  
  def create_routes(self, route_details, time, total_cars, output_dir):
    """
    Usage Example:
      n: ['-E2', 6], s: ['-E0', 6], e: '-E3', w: '-E1'
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
            edges = route_details[dir1][0] + ' ' + route_details[dir2][0]

          ET.SubElement(root, "route", id=f"route_{dir1}{dir2}", edges=edges)
          ET.SubElement(root, "flow", id=f"flow_{dir1}{dir2}", route=f"route_{dir1}{dir2}",
                          begin="0",end=str(time),
                          vehsPerHour=str(total_dir2),
                          departSpeed="max", departPos="base", departLane="best")
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, output_name)
    tree.write(output_file)
    print('Create Success')

  def save_to_csv(self, x_column_name, y_column_name, x_data, y_data, out_dir, name):
    df = pd.DataFrame({x_column_name: x_data, y_column_name: y_data})

    if not os.path.exists(out_dir):
      os.makedirs(out_dir)
    fullname = os.path.join(out_dir, name)   
    df.to_csv(f'{fullname}.csv', index=False)

  def simulation(self, route_file, useGui=False):
    if(useGui): sumoBinary = checkBinary('sumo-gui')
    else: sumoBinary = checkBinary('sumo')
    
    sumoCmd = [sumoBinary, "-n", self._net, "-r", route_file, "--no-warnings", "--quit-on-end"]
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

  def predict(self, route_file, model, useGui=False, yellow_time=4):
    env = self.create_environment(route_file, useGui, yellow_time)

    obs, info = env.reset()
    done = False
    waiting_time = {}

    while not done:
      env.render()
      action, _ = model.predict(obs)
      obs, reward, terminated, truncated, info = env.step(action)
      vehicles = traci.vehicle.getIDList()
      if len(vehicles) == 0: break
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

  def analyze_predict(self, model, dir, vphs, out_dir, useGui=False, yellow_time=4):

    """
    dir: 'trips/30minutes'
    vph: [3000, 3300, 3600]
    save csv data in {outdir}/{name} file
    """
    waiting_time = []
    clear_time = []

    for vph in vphs:
      total_waiting_time, total_clear_time = self.predict(f"{dir}/{vph}.rou.xml", model, useGui, yellow_time)
      waiting_time.append(total_waiting_time)
      clear_time.append(total_clear_time)
      print(f"{vph} cars: waiting time {total_waiting_time}, clear time: {total_clear_time}")

    self.save_to_csv('Vehicles Per Hour', 'Waiting time', vphs, waiting_time, out_dir, 'Waiting')
    self.save_to_csv('Vehicles Per Hour', 'Clear time', vphs, clear_time, out_dir, 'Clear')

  def analyze_fixed(self, dir, vphs, output_dir, useGui=False):
    waiting_time = []
    clear_time = []

    for vph in vphs:
      total_waiting_time, total_clear_time = self.simulation(f"{dir}/{vph}.rou.xml", useGui)
      waiting_time.append(total_waiting_time)
      clear_time.append(total_clear_time)
      print(f"{vph} cars: waiting time {total_waiting_time}, clear time: {total_clear_time}")

    self.save_to_csv('Vehicles Per Hour', 'Waiting time', vphs, waiting_time, output_dir, 'Waiting')
    self.save_to_csv('Vehicles Per Hour', 'Clear time', vphs, clear_time, output_dir, 'Clear')
