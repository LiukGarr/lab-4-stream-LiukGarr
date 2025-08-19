import json
import random

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from core.elements import Network

# Exercise Lab3: Network
ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'network.json'
f = open(file_input, 'r')
data = json.load(f)
nodi = []
vect_res_lat = []
vect_res_SNR = []
for nds in data:
    nodi.append(nds)
net = Network(data)
num_con = 100
draw = Network(data).draw()  # return the dataframe and the draw
i = 1
results = "Latency"
while i <= num_con:
    node1 = random.choice(nodi)
    node2 = random.choice(nodi)
    while node2 == node1:
        node2 = random.choice(nodi)
    dato_lat, dato_SNR = net.stream(node1, node2, results)
    if dato_lat != 0:
        vect_res_lat.append(float(dato_lat))
    if dato_SNR != "None":
        vect_res_SNR.append(dato_SNR)
    i += 1

print(f"# of paths found: {len(vect_res_lat)}")
print(f"For best {results}:\nAverage Lat.: {'{:.3e}'.format(np.average(vect_res_lat))}s, Average SNR: "
      f"{round(np.average(vect_res_SNR), 3)}dB")

plt.figure(2)
plt.hist(vect_res_lat, bins=i)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.title(f'Latency for best {results}')
plt.xlabel("Latency [s]")
plt.grid()

plt.figure(3)
plt.hist(vect_res_SNR, bins=i)
plt.title(f'SNR for best {results}')
plt.xlabel("SNR [dB]")
plt.grid()

plt.show()

f.close()
# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
