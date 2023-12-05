import os
import sys
import traci
from sumolib import checkBinary 
import utils

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


departIn = '30minutes'
vph_simu = [3000, 3300, 3600, 3900, 4200]

total_waiting_time = []
total_clear_time = []

sumoBinary = checkBinary('sumo')

for vph in vph_simu:
  sumoCmd = [sumoBinary, "-n", "2-intersection.net.xml", "-r", f'trips/{departIn}/{vph}-vph.rou.xml', "--no-warnings", "--quit-on-end"]
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

  total_waiting_time.append(total_time)
  total_clear_time.append(step)

  print(f'Simulation total waiting time: {total_time} seconds')
  print(f'Simulation total clear time: {step} seconds')

utils.save_to_csv('Vehicle Per Hour', 'Waiting Time', vph_simu, total_waiting_time, f'data/{departIn}/sim', 'waiting' )
utils.save_to_csv('Vehicle Per Hour', 'Clear Time', vph_simu, total_clear_time, f'data/{departIn}/sim', 'clear' )





