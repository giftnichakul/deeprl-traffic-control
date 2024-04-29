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

def getAlllanes(edge):
  return [lane for lane in allLanes if edge in lane]

def getEdgeWaitingTime(edge):
  return traci.edge.getWaitingTime(edge)

def totalVehicle(lanes: list):
  # traci.lane.getLastStepVehicleNumber -> total number of car in that lane
  numVehicleList = [traci.lane.getLastStepHaltingNumber(lane) for lane in lanes]
  return sum(numVehicleList)

net_file = './saint_paul/junction.net.xml'
route_path = f'./sn.rou.xml'

if(useGui): sumoBinary = checkBinary('sumo-gui')
else: sumoBinary = checkBinary('sumo')
sumoCmd = [sumoBinary, "-n", net_file, "-r", route_path, "--quit-on-end", "--waiting-time-memory", '10000', '--time-to-teleport', '-1']

traci.start(sumoCmd)

trafficLightId = traci.trafficlight.getIDList()[0]
allLanes = list(dict.fromkeys(traci.trafficlight.getControlledLanes(trafficLightId))) # remove duplicate
allPhases = traci.trafficlight.getAllProgramLogics(trafficLightId)[0].phases

switchTime = 10
currentPhase = 0
yellowPhase = True

north_lane = getAlllanes('E2')
south_lane = getAlllanes('E0')
east_lane = getAlllanes('E3')
west_lane = getAlllanes('E1')

"""
Index phases
- North -> 0 (E2)
- South -> 2 (E0)
- West -> 4 (E3)
- East -> 6 (E1)
"""

dir_lane = {0: north_lane, 1: south_lane, 2: east_lane, 3: west_lane}

waiting_time = {}

green_range = 60

print(traci.lane.getLength('-E2_0'), traci.lane.getLength('-E0_0'),traci.lane.getLength('-E1_0'), traci.lane.getLength('-E3_0'))

while traci.simulation.getMinExpectedNumber() > 0:
#while traci.simulation.getTime() < 600:
  traci.simulationStep()
  # find the next phases to open (yellow and green)
  c_time = traci.simulation.getTime()

  vehicles = traci.vehicle.getIDList()

  print('N', traci.edge.getLastStepVehicleIDs('-E2'))


  if '0' in vehicles:
    print(traci.vehicle.getSpeed('0'), c_time) # 1-388, 
  #print(c_time, traci.edge.getWaitingTime('-E0'), traci.edge.getLastStepHaltingNumber('-E0'))

  if c_time < 350:
    traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[0].state)
  elif c_time <= 350 + green_range:
    print(c_time, totalVehicle(south_lane))
    traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[2].state)
  elif c_time <= 350 + green_range + 5:
    print(c_time, totalVehicle(south_lane))
    traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[3].state)
  else:
    traci.trafficlight.setRedYellowGreenState(trafficLightId, allPhases[0].state)
  
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

"""
south lane 4:
เปิด 20s ไฟเหลือง 5s: รถจาก 168 เหลือ 130 ปล่อยรถ 38 ไฟเขียว 1s ปล่อยรถ 1.9
เปิด 50s ไฟเหลือง 5s: รถจาก 168 เหลือ 69 ปล่อยรถ 99 ไฟเขียว 1s ปล่อยรถ 1.98
เปิด 60s ไฟเหลือง 5s: รถจาก 168 เหลือ 60 ปล่อยรถ 108, ไฟเขียว 1s ปล่อยรถ 1.8 5

north lane 3:
เปิด 50s ไฟเหลือง 5s: รถจาก 168 เหลือ 99, 97 ปล่อยรถ 71 คัน, ไฟเขียว 1s ปล่อยรถ 1.42
เปิด 60s ไฟเหลือง 5s: รถจาก 168 เหลือ 85, 83 ปล่อยรถ 85 คัน, ไฟเขียว 1s ปล่อยรถ 1.41

east lane 2:
เปิด 50s ไฟเหลือง 5s: รถจาก 168 เหลือ 127, 126 ปล่อยรถ 42 คัน, ไฟเขียว 1s ปล่อยรถ 0.84
เปิด 60s ไฟเหลือง 5s: รถจาก 168 เหลือ 117, 117 ปล่อยรถ 51 คัน, ไฟเขียว 1s ปล่อยรถ 0.85

west lane 2:
เปิด 50s ไฟเหลือง 5s: รถจาก 168 เหลือ 124, 123 ปล่อยรถ 45 คัน, ไฟเขียว 1s ปล่อยรถ 0.9
เปิด 60s ไฟเหลือง 5s: รถจาก 168 เหลือ 115, 114 ปล่อยรถ 54 คัน, ไฟเขียว 1s ปล่อยรถ 0.9
"""
