import pandas as pd
import matplotlib.pyplot as plt

category = 'waiting'
column = 'Waiting'

# category = 'clear'
# column = 'Clear'

# Read the CSV files into pandas DataFrames
df1 = pd.read_csv(f'data/30minutes/sim/{category}.csv')
df2 = pd.read_csv(f'data/30minutes/pred/{category}.csv')

# Plot the data
plt.plot(df1['Vehicle Per Hour'], df1[f'{column} Time'], label=f'Simulation')
plt.plot(df2['Vehicle Per Hour'], df2[f'{column} Time'], label=f'Prediction')

# Add labels and title
plt.xlabel('Vehicles Per Hour')
plt.ylabel(f'Total{column} Time')
plt.title(f'Total {column} Time vs. Vehicles Per Hour')

# Add legend
plt.grid(True)
plt.legend()

# Show the plot
plt.show()
