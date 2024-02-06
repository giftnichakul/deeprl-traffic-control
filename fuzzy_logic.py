import os
import sys
import traci
from sumolib import checkBinary 

if 'SUMO_HOME' in os.environ:
  tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
  sys.path.append(tools)
else:
  sys.exit("please declare environment variable 'SUMO_HOME'")

# variable
useGui = False
fix_phase = True

def getAlllanes(edge):
  return [lane for lane in allLanes if edge in lane]

def totalVehicle(lanes: list):
  numVehicleList = [traci.lane.getLastStepVehicleNumber(lane) for lane in lanes]
  return sum(numVehicleList)

for i in [3000,]:
  net_file = './saint_paul/junction.net.xml'
  route_path = f'./saint_paul/1.0hour/trips/{i}.rou.xml'

  if(useGui): sumoBinary = checkBinary('sumo-gui')
  else: sumoBinary = checkBinary('sumo')
  sumoCmd = [sumoBinary, "-n", net_file, "-r", route_path, "--quit-on-end", "--waiting-time-memory", '10000', '--time-to-teleport', '-1']

  traci.start(sumoCmd)

  trafficLightId = traci.trafficlight.getIDList()[0]
  allLanes = list(dict.fromkeys(traci.trafficlight.getControlledLanes(trafficLightId))) # remove duplicate
  allPhases = traci.trafficlight.getAllProgramLogics(trafficLightId)[0].phases

  # Index phases:
  # North -> 0 (E2), South -> 2 (E0), West -> 4 (E3), East -> 6 (E1)

  switchTime = 15
  currentPhase = 0
  yellowPhase = True
  total_num_cars = []

  north_lane = getAlllanes('E2')
  south_lane = getAlllanes('E0')
  east_lane = getAlllanes('E3')
  west_lane = getAlllanes('E1') 

  waiting_time = {}
  num_lane = [3, 4, 2, 2]
  dir_lane = {0: north_lane, 1: south_lane, 2: west_lane, 3: east_lane}

  while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    #find the next phases to open (yellow and green)
    total_num_cars.append(traci.vehicle.getIDCount())

    if traci.simulation.getTime() == switchTime:
      # Swicth to green phase
      if yellowPhase:
        if fix_phase:
          currentPhase = (currentPhase + 1) % 4
          totalQueueCars = totalVehicle(dir_lane[currentPhase])
          switchTime += max(15, int(totalQueueCars / (0.45 * num_lane[currentPhase]))-5)
        else:
          numberVehicle = [totalVehicle(north_lane), totalVehicle(south_lane), totalVehicle(west_lane), totalVehicle(east_lane)]
          maxQueueNumber = max(numberVehicle)
          currentPhase = numberVehicle.index(maxQueueNumber) # get the direction that has the most number of cars
          # switchTime += max(15, int(maxQueueNumber / (0.45 * num_lane[currentPhase]))-5)
          if maxQueueNumber < 10: switchTime += 20
          elif maxQueueNumber < 20: switchTime += 30
          else: switchTime += 40
        yellowPhase = False
        traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[currentPhase*2].state)
      # Swicth to yellow phase before switch to green phase
      else:
        traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[currentPhase*2 + 1].state)
        switchTime += 5
        yellowPhase = True

    vehicles = traci.vehicle.getIDList()
    for vehicle in vehicles:
      vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
      if(vehicle not in waiting_time):
        waiting_time[vehicle] = vehicle_waiting_time
      else:
        waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
    total_clear_time = traci.simulation.getTime() 

  total_waiting_time = sum(waiting_time[vehicle] for vehicle in waiting_time)
  print(i, total_waiting_time, total_clear_time)
    
  traci.close()
