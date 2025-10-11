# coding: utf-8
import cPickle
import ast

input_file = 'data/original_data_499.csv'
output_file = 'data/trajectories_499.pkl'

all_trajs = []
with open(input_file, 'r') as f:
    header = f.readline()
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
    
        coords = ast.literal_eval(line)
        traj = []
        for idx, (lon, lat) in enumerate(coords):
            t = idx * 15
            traj.append([t, float(lon), float(lat)])
        all_trajs.append(traj)


with open(output_file, 'wb') as f:
    cPickle.dump(all_trajs, f, protocol=2)

print("Outputs: {}".format(output_file))
