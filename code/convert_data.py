# coding: utf-8
import cPickle
import ast

input_file = 'data/original_data_499.csv'
output_file = 'data/trajectories_499.pkl'

all_trajs = []
with open(input_file, 'r') as f:
    # 跳过第一行表头
    header = f.readline()
    for line in f:
        line = line.strip()
        if not line:
            continue
        # 去掉开头和结尾的引号
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        # 转为list
        coords = ast.literal_eval(line)
        traj = []
        for idx, (lon, lat) in enumerate(coords):
            t = idx * 15
            traj.append([t, float(lon), float(lat)])
        all_trajs.append(traj)

# 保存为pickle，和sim_trajectories风格一致
with open(output_file, 'wb') as f:
    cPickle.dump(all_trajs, f, protocol=2)

print("转换完成，输出文件: {}".format(output_file))
