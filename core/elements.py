import pandas as pd
import math
from core.parameters import c
from core.math_utils import snr
import matplotlib.pyplot as plt

occupied = []
arrow = '->'


class Signal_information(object):
    def __init__(self, sl, sn, path):
        self._signal_pow = 1e-3
        self._noise_pow = sn
        self._latency = sl
        self._path = path

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
        self._noise_pow += increment_np

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


class Connection(object):
    def __init__(self, node1, node2, sign_pow):
        self._input = node1
        self._output = node2
        self._signal_power = sign_pow
        self._latency = 0.0
        self._snr = 0.0
        pass

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, conn_lat):
        self._latency = conn_lat

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, conn_snr):
        self._snr = conn_snr


class Node(object):
    def __init__(self, lab_nds, pos, connected):
        self._lab_nds = lab_nds
        self._pos = pos
        self._connected = connected
        # pass

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
        # pass

    def propagate(self):
        pass


class Line(object):
    def __init__(self, lab_line, pos1, pos2):
        self._nextlines = []
        self._arr_1 = []
        self._arr_2 = []
        self.occupied_lines = []
        self._lab_line = lab_line
        self._arr_1 = pos1
        self._arr_2 = pos2

        # Length calculation
        diff_x = pow((float(self._arr_2[0]) - float(self._arr_1[0])), 2)
        diff_y = pow((float(self._arr_2[1]) - float(self._arr_1[1])), 2)
        self._length = math.sqrt(diff_x + diff_y)

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
        # pass

    def latency_generation(self):
        latency_gen = self.length / (c * 2 / 3)
        return latency_gen

    def noise_generation(self, sig_pow):
        noise = 1e-9*self.length*sig_pow
        return noise

    def propagate(self):
        pass

    def line_occupied(self):    # Lines
        self.occupied_lines = occupied
        return self.occupied_lines

    def line_state(self, state):    # Array of all the chosen lines
        if state == 0:
            i = True
            if len(occupied) == 0:
                occupied.append(self._lab_line)
            else:
                for occ_lines in occupied:
                    if self._lab_line == occ_lines:
                        i = False
                if i:
                    occupied.append(self._lab_line)

class Network(object):
    def __init__(self, data):
        self._nodes = {}
        self.line_occ = []
        self._lines = {}
        self._node2line = {}
        self._line2node = {}
        self.path = []
        self.lines_path = []
        self.path_mod = []
        self._sign_info = {}
        # Nodes, position and connected nodes gathering
        for nds in data:
            self._nodes[nds] = Node(nds, data[str(nds)]['position'], data[str(nds)]['connected_nodes'])
        # Lines definition
        for nds in self._nodes:
            for con_nds in self._nodes[nds].connected_nodes:
                line = nds + con_nds
                self._lines[line] = Line(line, self._nodes[nds].position, self._nodes[con_nds].position)
        self.connect()

        # Data-frame construction
        tabel = []
        self._sign_info = {}
        column_list = ["path", "total latency", "total noise", "SNR [dB]"]
        for id_node1 in self._nodes:
            for id_node2 in self._nodes:
                if id_node1 != id_node2:
                    for path in self.find_paths(id_node1, id_node2):
                        self._sign_info[path] = Signal_information(0.0, 0.0, path)
                        upd_lat, upd_noise = self.upgrade_lat_snr(path, self._sign_info[path])
                        snr_evaluated = round(snr(upd_noise), 3)
                        latency_eng = "{:.3e}".format(upd_lat)
                        noise_pow_eng = "{:.3e}".format(upd_noise)
                        row_list = [arrow.join(path), latency_eng, noise_pow_eng,
                                    snr_evaluated]
                        tabel.append(row_list)
        self._weighted_paths = pd.DataFrame(tabel, columns=column_list)
        print('Dataframe of all possible paths between all possible nodes: \n', self.weighted_paths())

    def nodes(self):
        return self._nodes

    def weighted_paths(self):
        return self._weighted_paths

    def upgrade_lat_snr(self, path, sign_info):
        # Latency and Noise calculation
        for x in range(len(path) - 1):
            to_check = path[x] + path[x + 1]
            noise = self._lines[to_check].noise_generation(sign_info.signal_power)
            lat = self._lines[to_check].latency_generation()
            sign_info.update_latency(lat)
            sign_info.update_noise_power(noise)
        upd_lat = sign_info.latency
        upd_noise = sign_info.noise_power
        return upd_lat, upd_noise

    def find_best_snr(self, paths):
        # Pathfinder for best-SNR method
        if paths == "NF":
            best_snr = 0
            best_path, best_lat = "None", "None"
        else:
            list_noise = []
            list_lat = []
            for path in paths:
                list_lat.append(self._sign_info[path].latency)
                list_noise.append(self._sign_info[path].noise_power)
            best_noise = min(list_noise)
            best_snr = round(snr(best_noise), 3)
            pos_best_noise = list_noise.index(best_noise)
            best_path = paths[pos_best_noise]
            best_lat = '{:.3e}'.format(list_lat[pos_best_noise])
            print(f"Best path {best_path}, SNR: {best_snr}, Lat.: {best_lat}")
        return best_lat, best_path, best_snr

    def find_best_latency(self, paths):
        # Pathfinder for best-latency method
        if paths == "NF":
            best_lat, best_path, best_snr = "None", "None", "None"
        else:
            list_noise = []
            list_lat = []
            for path in paths:
                list_lat.append(self._sign_info[path].latency)
                list_noise.append(self._sign_info[path].noise_power)
            best_lat = min(list_lat)
            pos_best_lat = list_lat.index(best_lat)
            best_lat = '{:.3e}'.format(min(list_lat))
            best_path = paths[pos_best_lat]
            best_snr = round(snr(list_noise[pos_best_lat]), 3)
        return best_lat, best_path, best_snr

    def stream(self, node1, node2, label):      # Research for a path to stream
        path_conn = Connection(node1, node2, Signal_information.signal_power)
        paths = self.find_paths(node1, node2)
        paths_tmp = paths.copy()

        # Remove of paths due to occupation
        for lines in self.line_occ:
            for path in paths:
                for i in range(len(path)-1):
                    lines_path = path[i]+path[i+1]
                    self.lines_path.append(lines_path)
                for line_path in self.lines_path:
                    if lines == line_path:
                        if len(self.path_mod) == 0:
                            self.path_mod.append(path)
                        else:
                            i = True
                            for mod in self.path_mod:
                                if path == mod:
                                    i = False
                            if i:
                                self.path_mod.append(path)
                self.lines_path.clear()
        for not_path in self.path_mod:
            paths_tmp.remove(not_path)
        self.path_mod.clear()

        # Method to implement best: Latency or SNR
        if label == "Latency":
            if len(paths_tmp) == 0:
                best_lat, best_path, best_snr = self.find_best_latency("NF")
                dato = [0, "None"]
            else:
                best_lat, best_path, best_snr = self.find_best_latency(paths_tmp)
                dato = [best_lat, best_snr]
        else:
            if len(paths_tmp) == 0:
                best_lat, best_path, best_snr = self.find_best_snr("NF")
                dato = [0, "None"]
            else:
                best_lat, best_path, best_snr = self.find_best_snr(paths_tmp)
                dato = [best_lat, best_snr]

        # Propagate the found path
        if dato[1] != 0 and dato[0] != "None" and best_path != "None":
            self.propagate(best_path, 0)
            path_conn.latency = best_lat
            path_conn.snr = best_snr
        return dato

    @property
    def lines(self):
        return self._lines

    def draw(self):

        # Network map and plot
        for id_node in self._nodes:
            x0 = self._nodes[id_node].position[0]
            y0 = self._nodes[id_node].position[1]
            plt.plot(x0, y0, 'yo', markersize=10)
            plt.text(x0 + 20, y0 + 20, id_node)

            for con_node in self._nodes[id_node].connected_nodes:
                x1 = self._nodes[con_node].position[0]
                y1 = self._nodes[con_node].position[1]
                plt.plot([x0, x1], [y0, y1], 'r')
        plt.figure(1)
        plt.title('Network')
        plt.xlabel('X[m]')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        plt.ylabel('Y[m]')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        plt.grid()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        paths = []
        visited = []
        first_node = label1
        last_node = label2
        b_stop = False

        # Pathfinder method
        for nds in self._node2line:
            if nds == first_node:
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
            return paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        self._node2line = {}
        self._line2node = {}
        line2node = {}
        for nds in self._nodes:
            for lns in self._lines:
                char = lns[0]
                if nds == char:
                    self._node2line.setdefault(nds, []).append(lns)
        for lns in self._lines:
            char2 = lns[1]
            for nds in self._nodes:
                if nds == char2:
                    n = nds
                    self._line2node.setdefault(lns, []).append(n)
            line2node.setdefault(lns, []).append(self._line2node[lns])
        pass

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, path, state):
        for x in range(len(path)-1):
            line = path[x]+path[x+1]
            self._lines[line].line_state(state)
            self.line_occ = self._lines[line].line_occupied()
        pass
