import os
import sys

import gymnasium as gym
from stable_baselines3.dqn.dqn import DQN
import traci
import pandas as pd

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

from sumo_rl import SumoEnvironment

# parameter
model_name = 'model/30minutes/3600-vph.zip'
route_file = 'trips/30minutes/4200-vph.rou.xml'
useGui = True

env = SumoEnvironment(
    net_file="2-intersection.net.xml",
    route_file=route_file,
    single_agent=True,
    use_gui=useGui,
    yellow_time=4,
)

model = DQN.load(model_name, env=env)

obs, info = env.reset()
done = False
waiting_time = {}

while not done:
    env.render()
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    vehicles = traci.vehicle.getIDList()
    step = traci.simulation.getTime()
    if len(vehicles) == 0: break
    for vehicle in vehicles:
      vehicle_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle)
      if(vehicle not in waiting_time):
        waiting_time[vehicle] = vehicle_waiting_time
      else:
        waiting_time[vehicle] = max(vehicle_waiting_time, waiting_time[vehicle])
    done = terminated or truncated

total_waiting_time = sum(waiting_time[vehicle] for vehicle in waiting_time)

env.close()
print(f'Predict total waiting time: {total_waiting_time} seconds')
print(f'Predict total clear time: {step} seconds')
