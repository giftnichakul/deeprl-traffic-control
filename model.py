import os
import sys

import gymnasium as gym
from stable_baselines3.dqn.dqn import DQN

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

from sumo_rl import SumoEnvironment

# parameter
route_number = '5000'
net_file="./saint_paul/simulation_saintpaul.net.xml"
route_file = f"./saint_paul/trips/1hour/{route_number}.rou.xml"
total_timesteps = 10000
output_folder = "./saint_paul/model/1hour/"

def my_reward_fn(traffic_signal):
    return traffic_signal.get_total_queued()

env = SumoEnvironment(
    net_file=net_file,
    route_file=route_file,
    single_agent=True,
    yellow_time=5,
    num_seconds=7000,
    delta_time=6,
    #reward_fn=my_reward_fn
)

model = DQN(
    env=env,
    policy="MlpPolicy",
    learning_starts=0,
    train_freq=1,
    exploration_initial_eps=0.05,
    exploration_final_eps=0.01,
    verbose=1
)

total_timesteps = total_timesteps
model.learn(total_timesteps=total_timesteps, reset_num_timesteps=False)
model.save(f"{output_folder}/{route_number}")

env.close()
