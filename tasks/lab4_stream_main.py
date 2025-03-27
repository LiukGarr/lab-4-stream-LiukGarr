import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from core.elements import Network
from core.elements import Signal_information

# Exercise Lab3: Network
ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'
f = open(file_input, 'r')
data = json.load(f)
net = Network(data)
node1 = 'E'
node2 = 'B'
print(f"Path between {node1} and {node2}: \n", net.find_paths(node1, node2))
draw = Network(data).draw() # return the dataframe and the draw








f.close()
# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
