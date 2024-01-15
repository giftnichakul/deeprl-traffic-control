import os
import sys
import traci
from sumolib import checkBinary 

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# parameter
route_file = './saint_paul/trips/1hour/3000.rou.xml'
net_file = "./saint_paul/simulation_saintpaul.net.xml"

sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, "-n", net_file, "-r", route_file, "--no-warnings", "--quit-on-end"]
traci.start(sumoCmd)

step = 0
waiting_time = {}
cars = set()

while traci.simulation.getMinExpectedNumber() > 0:
  traci.simulationStep()
  vehicles = traci.vehicle.getIDList()
  for vehicle in vehicles:
    cars.add(vehicle)
    vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
    if(vehicle not in waiting_time):
      waiting_time[vehicle] = vehicle_waiting_time
    else:
      waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
  step = traci.simulation.getTime()  
    
traci.close()
total_time = sum(waiting_time[vehicle] for vehicle in waiting_time)
print(f'Simulation total waiting time: {total_time} seconds')
print(f'Simulation total clear time: {step} seconds')
