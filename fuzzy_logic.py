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
for i in [1000, 2000, 3000, 4000, 5000]:
  net_file = './saint_paul/junction.net.xml'
  route_path = f'./saint_paul/1.0hour/trips/{i}.rou.xml'

  if(useGui): sumoBinary = checkBinary('sumo-gui')
  else: sumoBinary = checkBinary('sumo')
  sumoCmd = [sumoBinary, "-n", net_file, "-r", route_path, "--quit-on-end", "--waiting-time-memory", '10000', '--time-to-teleport', '-1']

  traci.start(sumoCmd)

  trafficLightId = traci.trafficlight.getIDList()[0]
  allLanes = list(dict.fromkeys(traci.trafficlight.getControlledLanes(trafficLightId))) # remove duplicate
  allPhases = traci.trafficlight.getAllProgramLogics(trafficLightId)[0].phases

  swithTime = 10
  currentPhase = 0
  yellowPhase = True

  def getAlllanes(edge):
    return [lane for lane in allLanes if edge in lane]

  def totalVehicle(lanes: list):
    numVehicleList = [traci.lane.getLastStepVehicleNumber(lane) for lane in lanes]
    return sum(numVehicleList)

  north_lane = getAlllanes('E2')
  south_lane = getAlllanes('E0')
  east_lane = getAlllanes('E3')
  west_lane = getAlllanes('E1')

  """
  Index phases
  - North -> 0 (E2)
  - South -> 2 (E2)
  - West -> 4 (E2)
  - East -> 6 (E2)
  """

  waiting_time = {}

  #while traci.simulation.getTime() < 700:
  while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    #find the next phases to open (yellow and green)
    if traci.simulation.getTime() == swithTime:
      # Swicth to green phase
      if yellowPhase:
        numberVehicle = [totalVehicle(north_lane), totalVehicle(south_lane), totalVehicle(west_lane), totalVehicle(east_lane)]
        maxQueueNumber = max(numberVehicle)
        currentPhase = numberVehicle.index(maxQueueNumber) # get the direction that has the most number of cars
        yellowPhase = False

        if maxQueueNumber < 10:
          swithTime += 20
        elif maxQueueNumber < 20:
          swithTime += 30
        else:
          swithTime += 40

        swithTime += 20
        traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[currentPhase*2].state)
      # Swicth to yellow phase before switch to green phase
      else:
        traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[currentPhase*2 + 1].state)
        swithTime += 5
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
