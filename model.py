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

def my_reward_fn(traffic_signal):
    return traffic_signal.get_total_queued()

route_file = '3600-vph'
env = SumoEnvironment(
    net_file="2-intersection.net.xml",
    route_file=f"trips/30minutes/{route_file}.rou.xml",
    single_agent=True,
    yellow_time=4,
    num_seconds=3000,
    delta_time=5,
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

total_timesteps = 6000
model.learn(total_timesteps=total_timesteps, reset_num_timesteps=False)
model.save(f"model/30minute/{route_file}")

env.close()
