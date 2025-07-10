import json
import random

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
nodi = []
# vect_res = []
vect_res_lat_4Lat = []
vect_res_lat_4SNR = []
vect_res_SNR_4Lat = []
vect_res_SNR_4SNR = []
for nds in data:
    nodi.append(nds)
net = Network(data)
num_con = 100
# node1 = 'A'
# node2 = 'A'
# print(f"Path between {node1} and {node2}: \n", net.find_paths(node1, node2))
draw = Network(data).draw()  # return the dataframe and the draw
i = 1
results = ["SNR", "Latency"]
while i <= num_con:
    node1 = random.choice(nodi)
    node2 = random.choice(nodi)
    if node2 == node1:
        node2 = random.choice(nodi)
    dato_lat_4SNR, dato_SNR_4SNR = net.stream(node1, node2, results[0])
    dato_lat_4Lat, dato_SNR_4Lat = net.stream(node1, node2, results[1])
    if dato_lat_4Lat != 0:
        # print(f"{dato_lat_4Lat}s")
        vect_res_lat_4Lat.append(float(dato_lat_4Lat))
    if dato_lat_4SNR != 0:
        # print(f"{dato_lat_4SNR}s")
        vect_res_lat_4SNR.append(float(dato_lat_4SNR))
    if dato_SNR_4Lat != "None":
        # print(f"{dato_SNR_4Lat}dB")
        vect_res_SNR_4Lat.append(dato_SNR_4Lat)
    if dato_SNR_4SNR != "None":
        # print(f"{dato_SNR_4SNR}dB")
        vect_res_SNR_4SNR.append(dato_SNR_4SNR)
    # if (dato_SNR != "None") and (dato_lat != 0):
    # vect_res_lat.append(dato_lat)
    i += 1
avg_Lat_4Lat = '{:.3e}'.format(sum(vect_res_lat_4Lat)/len(vect_res_lat_4Lat))
avg_SNR_4Lat = round(sum(vect_res_SNR_4Lat)/len(vect_res_SNR_4Lat), 3)

avg_Lat_4SNR = '{:.3e}'.format(sum(vect_res_lat_4SNR)/len(vect_res_lat_4SNR))
avg_SNR_4SNR = round(sum(vect_res_SNR_4SNR)/len(vect_res_SNR_4SNR), 3)

print("Avg. values for best Latency:")
print(f"Avg. Latency: {avg_Lat_4Lat}s, Avg. SNR: {avg_SNR_4Lat}dB")

print("Avg. values for best SNR:")
print(f"Avg. Latency: {avg_Lat_4SNR}s, Avg. SNR: {avg_SNR_4SNR}dB")

fig, axs = plt.subplots(1, 2)
fig.suptitle('Latency and SNR for best SNR')
axs[0].hist(vect_res_lat_4SNR, bins=i)
axs[0].ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
axs[0].set_title('Latency [s]')
axs[0].grid()
axs[1].hist(vect_res_SNR_4SNR, bins=i)
axs[1].set_title('SNR [dB]')
axs[1].grid()

fig, axs = plt.subplots(1, 2)
fig.suptitle('Latency and SNR for best latency')
axs[0].hist(vect_res_lat_4Lat, bins=i)
axs[0].ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
axs[0].set_title('Latency [s]')
axs[0].grid()
axs[1].hist(vect_res_SNR_4Lat, bins=i)
axs[1].set_title('SNR [dB]')
axs[1].grid()

# plt.show()

# best_path, best_snr = net.find_best_snr(node1, node2)
# print(f"Best path between {node1} and {node2}, is {best_path} with snr= {best_snr}dB")
# best_path, best_lat = net.find_best_latency(node1, node2)
# print(f"Best path between {node1} and {node2}, is {best_path} with latency= {best_lat}s")


f.close()
# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
