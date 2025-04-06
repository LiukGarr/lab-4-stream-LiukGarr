# import json
import pandas as pd
import math
from core.parameters import c
from core.math_utils import snr
from decimal import Decimal
import matplotlib.pyplot as plt

occupied = []
arrow = '->'


class Signal_information(object):
    def __init__(self, sl, sn, path):
        self._signal_pow = 1e-3
        self._noise_pow = sn
        self._latency = sl
        self._path = path
        pass

    @property
    def signal_power(self):
        return self._signal_pow

    def update_signal_power(self, increment_sp):
        self._signal_pow += increment_sp

    @property
    def noise_power(self):
        return self._noise_pow

    @noise_power.setter
    def noise_power(self, np):
        self._noise_pow = np

    def update_noise_power(self, increment_np):
        self._noise_pow = self._noise_pow + increment_np

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, lat):
        self._latency = lat

    def update_latency(self, increment_lat):
        self._latency = self._latency + increment_lat

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, selected_path):
        self._path = selected_path

    def update_path(self):
        tmp_list_path = [self._path[0][1:]]
        self._path = tmp_list_path


class Connection(object):
    def __init__(self, node1, node2, sign_pow, lat, sig_noise_rate, path):
        self.input = node1
        self.output = node2
        self.signal_power = sign_pow
        self.latency = lat
        self.snr = sig_noise_rate
        print(f"Input node {self.input}, Output node {self.output}; Chosen path {path}")
        pass


class Node(object):
    def __init__(self, lab_nds, pos, connected):
        self._lab_nds = lab_nds
        self._pos = pos
        self._connected = connected
        pass

    @property
    def label(self):
        return self._lab_nds

    @property
    def position(self):
        return self._pos

    @property
    def connected_nodes(self):
        return self._connected

    @property
    def successive(self):
        return self._nextnds

    @successive.setter
    def successive(self, next_line):
        self._nextnds = next_line
        pass

    def propagate(self):
        pass


class Line(object):
    def __init__(self, lab_line, pos1, pos2, state):
        self._nextlines = []
        self._arr_1 = []
        self._arr_2 = []
        self.occupied_lines = []
        self._lab_line = lab_line
        self._arr_1 = pos1
        self._arr_2 = pos2
        self.state = state
        # print(float(self._arr_1[0]), float(self._arr_1[1]))
        diff_x = pow((float(self._arr_2[0]) - float(self._arr_1[0])), 2)
        diff_y = pow((float(self._arr_2[1]) - float(self._arr_1[1])), 2)
        self._length = math.sqrt(diff_x + diff_y)
        if self.state == 1:
            i = True
            # print(f"Starting occupation: {len(occupied)}")
            if len(occupied) == 0:
                occupied.append(lab_line)
                occupied.append(lab_line[1]+lab_line[0])
            else:
                for occ_lines in occupied:
                    if lab_line == occ_lines:
                        i = False
                if i:
                    occupied.append(lab_line)
                    occupied.append(lab_line[1] + lab_line[0])
            # print(f"Occupied lines: {occupied}")
        # print(diff_x, diff_y)
        pass

    @property
    def label(self):
        return self._lab_line

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._nextlines

    @successive.setter
    def successive(self, next_node):
        self._nextlines = next_node
        pass

    def latency_generation(self, length_line):
        latency_gen = length_line / (c * 2 / 3)
        return latency_gen

    def noise_generation(self, signal_power, length_line):
        noise = 1e-9*length_line*signal_power
        #print(noise)
        return noise

    def propagate(self):
        pass

    def line_occupied(self):
        self.occupied_lines = occupied
        return self.occupied_lines

class Network(object):
    def __init__(self, data):
        self.line_occ = []
        self.path_founded=[]
        self._nodes = {}
        self.line_occ = []
        self._lines = {}
        self._node2line = {}
        self._line2node = {}
        self.path = []
        for nds in data:
            self._nodes[nds] = Node(nds, data[str(nds)]['position'], data[str(nds)]['connected_nodes'])
            # nodi.setdefault(nds, []).extend((self._nodes[nds].label, self._nodes[nds].connected_nodes, self._nodes[nds].position))
            # print(nodi[nds])
            # print(f"label: {self._nodes[nds].label}, pos: {self._nodes[nds].position}, connection: {self._nodes[nds].connected_nodes}")
        for nds in self._nodes:
            for con_nds in self._nodes[nds].connected_nodes:
                line = nds + con_nds
                # lst_linee.append(line)
                # pos1 = self._nodes[nds].position
                # pos2 = self._nodes[con_nds].position
                self._lines[line] = Line(line, self._nodes[nds].position, self._nodes[nds].position, 0)
                # print(f"Nodo 1: {self._nodes[nds].label}, Nodo 2: {self._nodes[con_nds].label}")
                # print(f"La distanza {self._lines[line].label} è {self._lines[line].length} meters'")
        # print(nodi, "\n", linee)
        self.connect()
        #self._weighted_paths = pd.DataFrame(tabel, columns=column_list)
        #self._weighted_paths = self._weighted_paths.set_index("path", drop=False)

    def nodes(self):
        return self._nodes

    def weighted_paths(self):
        path_separ = "->"
        tabel = []
        column_list = ["path", "total latency", "total noise", "SNR [dB]"]
        for id_node1 in self._nodes:
            for id_node2 in self._nodes:
                if id_node1 != id_node2:
                    for path in self.find_paths(id_node1, id_node2):
                        sign_info = Signal_information(0.0, 0.0, path)
                        self.propagate(sign_info, path, 0)
                        # self.probe(sign_info)
                        snr_evaluated = round(snr(sign_info.signal_power, sign_info.noise_power), 3)
                        latency_eng = "{:.3e}".format(sign_info.latency)
                        noisepow_eng = "{:.3e}".format(sign_info.noise_power)
                        row_list = [path_separ.join(path), latency_eng, noisepow_eng,
                                    snr_evaluated]
                        tabel.append(row_list)
        df = pd.DataFrame(tabel, columns=column_list)
        print('Dataframe of all possible paths between all possible nodes: \n', df)
        pass

    def find_best_snr(self, lab_nod1, lab_nod2, paths):
        best_snr = 0.0
        for path in paths:
            sign_info = Signal_information(0.0, 0.0, path)
            self.propagate(sign_info, path, 0)
            snr_evaluated = snr(sign_info.signal_power, sign_info.noise_power)
            #print(f"{path} \t {round(snr_evaluated, 3)}dB")
            if float(best_snr) < float(snr_evaluated):
                best_snr = round(snr_evaluated, 3)
        return best_snr

    def find_best_latency(self, paths):
        best_lat = 1
        if paths == "NF":
            best_lat = "NONE"
            best_path = "NONE"
        else:
            for path in paths:
                sign_info = Signal_information(0.0, 0.0, path)
                self.propagate(sign_info, path,0)
                #print(f"{path} \t {'{:.3e}'.format(sign_info.latency)}s")
                if float(sign_info.latency) < float(best_lat):
                    best_path = path
                    best_lat = sign_info.latency
        return best_lat, best_path

    def stream(self, node1, node2, label):
        paths = self.find_paths(node1, node2)
        paths_tmp = paths
        # print(f"All possible paths: {paths}")
        # print(f"Chosen path: {paths}")
        if len(self.line_occ) != 0:
            if len(paths) != 0:
                for lines in self.line_occ:
                    for path in paths_tmp:
                        for x in range(len(path)-1):
                            if lines == path[x]+path[x+1]:
                                path_ind = paths.index(path)
                                #print(f"Elements deleted: {path} at index {path_ind}")
                                paths_tmp.pop(path_ind)
                # print(f"Reduced path: {paths_tmp}")
        #print(f"Paths remains: {paths}")
        sign_info = Signal_information(0.0, 0.0, paths_tmp)
        if label == "Latency":
            if len(paths) == 0:
                best_lat, best_path = self.find_best_latency("NF")
                Connection(node1, node2, sign_info.signal_power, best_lat, "NONE", best_path)
                dato = "NONE"
            else:
                best_lat, best_path = self.find_best_latency(paths_tmp)
                # print(f"Best streaming path: {best_path}")
                # self.path_founded.append(best_path)
                # print(f"Chosen path: {self.path_founded}")
                #print(f"Best Latency: {best_lat}s; Best path: {best_path}")
                self.propagate(sign_info, best_path, 1)
                Connection(node1, node2, sign_info.signal_power, "{:.3e}".format(best_lat), "NONE", best_path)
                dato = best_lat
        else:
            best_snr = self.find_best_snr(node1, node2, paths)
            Connection(node1, node2, sign_info.signal_power, "NONE", best_snr, paths)
            dato = best_snr

        return dato
    @property
    def lines(self):
        return self._lines

    def draw(self):
        self.weighted_paths()
        for id_node in self._nodes:
            x0 = self._nodes[id_node].position[0]
            y0 = self._nodes[id_node].position[1]
            plt.plot(x0, y0, 'yo', markersize=10)
            plt.text(x0 + 20, y0 + 20, id_node)

            for con_node in self._nodes[id_node].connected_nodes:
                x1 = self._nodes[con_node].position[0]
                y1 = self._nodes[con_node].position[1]
                plt.plot([x0, x1], [y0, y1], 'r')

        plt.title('Network')
        plt.xlabel('X[m]')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        plt.ylabel('Y[m]')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        plt.grid()
        plt.show()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        path = []
        paths = []
        visited = []
        copy_n2l = {}
        copy_l2n = {}
        first_node = label1
        last_node = label2
        b_stop = False
        for nds in self._node2line:
            if nds == first_node:
                # print(f"Le linee attaccate a {self._first_node} sono {self._node2line[nds]}")
                b_stop = True
        if not b_stop:
            print("Invalid node")
        else:
            visited.append(first_node)
            for next_lns in self._node2line[first_node]:
                next_nds = self._line2node[next_lns][0]
                visited.append(next_nds)
                if next_nds == last_node:
                    paths.append(first_node + next_nds)
                else:
                    for next_lns in self._node2line[next_nds]:
                        if next_lns[1] != first_node:
                            if next_lns[1] == last_node:
                                paths.append(first_node + next_nds + self._line2node[next_lns][0])
                            else:
                                next_nds1 = self._line2node[next_lns][0]
                                visited.append(next_nds1)
                                for next_lns1 in self._node2line[next_nds1]:
                                    if next_lns1[1] == last_node:
                                        paths.append(first_node + next_nds + self._line2node[next_lns][0] +
                                                     self._line2node[next_lns1][0])
                                    else:
                                        if (next_lns1[1] != next_nds) and (next_lns1[1] != first_node):
                                            next_nds2 = self._line2node[next_lns1][0]
                                            for next_lns2 in self._node2line[next_nds2]:
                                                if next_lns2[1] == last_node:
                                                    paths.append(first_node + next_nds + self._line2node[next_lns][0] +
                                                                 self._line2node[next_lns1][0] +
                                                                 self._line2node[next_lns2][0])
                                                else:
                                                    if (next_lns2[1] != next_nds) and (next_lns2[1] != first_node):
                                                        next_nds3 = self._line2node[next_lns2][0]
                                                        for next_lns3 in self._node2line[next_nds3]:
                                                            if next_lns3[1] == last_node:
                                                                tmp = first_node + next_nds + self._line2node[next_lns][
                                                                    0] + self._line2node[next_lns1][0]
                                                                if not self._line2node[next_lns2][0] in tmp:
                                                                    paths.append(first_node + next_nds +
                                                                                 self._line2node[next_lns][0] +
                                                                                 self._line2node[next_lns1][0] +
                                                                                 self._line2node[next_lns2][0] +
                                                                                 self._line2node[next_lns3][0])
            #print(Signal_information(paths).path)
            #print(f"Paths between {label1} and {label2}: \n", paths)
            #self.propagate()
            return paths
            #pass

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        self._node2line = {}
        node2line = {}
        self._line2node = {}
        line2node = {}
        for nds in self._nodes:
            for lns in self._lines:
                char = lns[0]
                if nds == char:
                    self._node2line.setdefault(nds, []).append(lns)
            # node2line.setdefault(nds, []).append(self._node2line[nds])
        # print(node2line)
        for lns in self._lines:
            # char1 = lns[0]
            char2 = lns[1]
            for nds in self._nodes:
                # if nds == char1:
                # n1 = nds
                # self._line2node.setdefault(lns, []).insert(0, n1)
                # if nds == char2:
                # n2 = nds
                # self._line2node.setdefault(lns, []).insert(1, n2)
                if nds == char2:
                    n = nds
                    self._line2node.setdefault(lns, []).append(n)
            line2node.setdefault(lns, []).append(self._line2node[lns])
        #print('Connection: \n', line2node)
        pass

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information, path, state):
        #self._lines[line] = Line(line, self._nodes[nds].position, self._nodes[con_nds].position)
        #print(path)
        for x in range(len(path)-1):
            line = path[x]+path[x+1]
            if state == 1:
                # print(f"Lines in best path: {line}")
                lin_length = Line(line, self._nodes[path[x]].position, self._nodes[path[x+1]].position, state)
                self.line_occ = lin_length.line_occupied()
            else:
                lin_length = Line(line, self._nodes[path[x]].position, self._nodes[path[x + 1]].position, state)
            noise = lin_length.noise_generation(signal_information.signal_power, lin_length.length)
            latency = lin_length.latency_generation(lin_length.length)
            #print(f"Partial results: Length: {'{:.3e}'.format(lin_length.length)}, noise: {'{:.3e}'.format(noise)}, latency: {'{:.3e}'.format(latency)}")
            signal_information.update_noise_power(noise)
            signal_information.update_latency(latency)
            #print(f"Line {line} --> line length: {'{:.3e}'.format(lin_length.length)}m noise_pow: {'{:.3e}'.format(signal_information.noise_power)}mW; latency: {'{:.3e}'.format(signal_information.latency)}s")
            #print(f"Nodo 1: {self._nodes[path[x]].label}, Nodo 2: {self._nodes[path[x+1]].label}")
            #print(f"Length between {self._lines[line].label} is {self._lines[line].length} meters and noise power is {signal_information.noise_power} ")
        #print(f"Length betwwen {node1} and {node2}: ", lin_length)
        pass
