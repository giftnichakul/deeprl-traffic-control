# Depprl-traffic-control

This is the project that try to improve the traffic by using deep reinforcement learning. We train the model in 2 intersection road.
![image](https://github.com/giftnichakul/depprl-traffic-control/assets/70993304/893ad3db-9948-440a-a11d-4d722d8d4f6b)

## Explain trips
- 30 minutes means all vehicles can depart since 0 to 30 minutes
- 3000-vph means 3000 vehicles per hours
- you can change begin, end and vehsPerHour 

## Simulation in sumo-gui
- sumo-gui: simulation.sumocfg
  - config the net and route file in simulation.sumocfg
  - open the file in sumo-gui and run
- using python: one-simulation.py
  - config the route_file variable in one-simulation.py
  - if you dont want to see the simulation change checkBinary(sumo-gui) to checkBinary(sumo) 
  - run ```python one-simulation.py```

## Train the model
- use model.py
  - config the SumoEnvironement: net-file, route-file, num_seconds(time you want to train)
  - config the model ex. DQN
  - config the path you want to save the model
  - run ```python model.py```
    
## Test the model
- use one-predict.py
  - config the model_name and route_file you want to test
  - if you want to see the simulation set the useGui=True
  - run ```python one-predict.py```

## Save th data
- use analyze-simulation.py to save the fixed traffic data
  - config the departIn, vph_simu you want to test
  - if you want to see the simulation set the checkBinray(sumo-gui)
  - run ```python analyze-simulation.py```
  - the result will be csv file in folder data
- use analyze-predict.py to save the predict traffic data
  - config the departIn, vph_simu you want to test
  - if you want to see the simulation set the checkBinray(sumo-gui)
  - run ```python analyze-predict.py```
  - the result will be csv file in folder data


