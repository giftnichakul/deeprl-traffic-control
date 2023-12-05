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
plt.plot(df1['Vehicle Per Hour'], df1[f'{column} Time'], label=f'Simulation {category}')
plt.plot(df2['Vehicle Per Hour'], df2[f'{column} Time'], label=f'Prediction {category}')

# Add labels and title
plt.xlabel('VPH')
plt.ylabel(f'{column} Time')
plt.title(f'{column} Time vs. VPH')

# Add legend
plt.grid(True)
plt.legend()

# Show the plot
plt.show()
