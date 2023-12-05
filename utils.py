import matplotlib.pyplot as plt
import pandas as pd
import traci
import numpy as np
import os

def plot(x, y, xlabel, ylabel, folder,min_time='', max_time='',show=False):
  plt.clf()
  plt.plot(x, y, marker='o', linestyle='-', color='b')
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.title(f'{xlabel} vs. {ylabel}')
  plt.grid(True)
  
  os.makedirs(folder, exist_ok=True)
  plt.savefig(os.path.join(folder, f'{xlabel}-{ylabel}.png'))
  show and plt.show()

def get_system_info():
  vehicles = traci.vehicle.getIDList()
  speeds = [traci.vehicle.getSpeed(vehicle) for vehicle in vehicles]
  acc_waiting_times = [traci.vehicle.getAccumulatedWaitingTime(vehicle) for vehicle in vehicles]
 
  return {
    "system_total_stopped": sum(int(speed < 0.1) for speed in speeds),
    "system_total_waiting_time": sum(acc_waiting_times),
    "system_mean_waiting_time": 0.0 if len(vehicles) == 0 else np.mean(acc_waiting_times),
    "system_mean_speed": 0.0 if len(vehicles) == 0 else np.mean(speeds),
  }

def save_to_csv(x_column, y_column, x_data, y_data, out_dir, name):
  df = pd.DataFrame({x_column: x_data, y_column: y_data})

  if not os.path.exists(out_dir):
      os.mkdir(out_dir)

  fullname = os.path.join(out_dir, name)   
  df.to_csv(f'{fullname}.csv', index=False)


def plot_compare_graph(sim_file, pred_file):
  df1 = pd.read_csv(sim_file)
  df2 = pd.read_csv(pred_file)

  # Merge the DataFrames based on the common column (assuming it's named 'vph')
  merged_df = pd.merge(df1, df2, on='vph')

  # Plot the data
  plt.plot(merged_df['vph'], merged_df['first_waiting'], label='First Waiting')
  plt.plot(merged_df['vph'], merged_df['second_waiting'], label='Second Waiting')

  # Add labels and title
  plt.xlabel('VPH')
  plt.ylabel('Waiting Time')
  plt.title('Waiting Time vs. VPH')

  # Add legend
  plt.legend()

  # Show the plot
  plt.show()
