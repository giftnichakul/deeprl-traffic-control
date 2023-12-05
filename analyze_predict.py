import os
import sys
import traci
import utils
from sumo_rl import SumoEnvironment
from stable_baselines3.dqn.dqn import DQN

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


departIn = '30minutes'
vph_simu = [3900, 4200]
model_name = '3600-vph.zip'

total_waiting_time = []
total_clear_time = []

for vph in vph_simu:
  env = SumoEnvironment(
    net_file="2-intersection.net.xml",
    route_file=f'trips/{departIn}/{vph}-vph.rou.xml',
    single_agent=True,
    yellow_time=4,
  )
  model = DQN.load(f'model/{departIn}/{model_name}', env=env)

  obs, info = env.reset()
  done = False
  waiting_time = {}

  while not done:
    env.render()
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    vehicles = traci.vehicle.getIDList()
    if len(vehicles) == 0 and step > 1800: break
    for vehicle in vehicles:
      vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
      if(vehicle not in waiting_time):
        waiting_time[vehicle] = vehicle_waiting_time
      else:
        waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
    step = traci.simulation.getTime()
    done = terminated or truncated

  total_time = sum(waiting_time[vehicle] for vehicle in waiting_time)
  
  total_waiting_time.append(total_time)
  total_clear_time.append(step)

  print(f'Simulation total waiting time: {total_time} seconds')
  print(f'Simulation total clear time: {step} seconds')

#utils.save_to_csv('Vehicle Per Hour', 'Waiting Time', vph_simu, total_waiting_time, f'data/{departIn}/pred/', 'waiting' )
#utils.save_to_csv('Vehicle Per Hour', 'Clear Time', vph_simu, total_clear_time, f'data/{departIn}/pred/', 'clear' )
