import argparse
import numpy as np
import matplotlib.pyplot as plt

def numify(s):
    try:
        return float(s)
    except ValueError:
        return s


parser = argparse.ArgumentParser(description='Generate a set of jump arcs.')
parser.add_argument('--name', type=str, default='SMB',
                    help='The name of the game/character to generate jumps for')
parser.add_argument('--file', type=str, default='HAS.csv',
                    help='The file to load the jump parameters from')
parser.add_argument('--num',type=int,default = 2,
                    help='The number of jumps to perform')
parser.add_argument('--floor',type=int,default = 0,
                    help='The height at which to stop the falls')
parser.add_argument('--tilesize',type=int,default = 16,
                    help='The tile size in pixels')
parser.add_argument('--speed',type=int,default = 10,
                    help='The maximum x speed for a jump in tiles per second')

args = parser.parse_args()

data = {}
with open(args.file) as ha_file:
    header = ha_file.readline().rstrip()
    categories = header.split('\t')
    ind2cat = {ii:cat.replace('"','') for ii, cat in enumerate(categories)}
    for line in ha_file:
        line = [tok.replace('"','') for tok in line.rstrip().split('\t')]


        data[line[0]] = {ind2cat[ii]:numify(tok) for ii, tok in enumerate(line)}


import numpy as np
if args.name not in data:
    print(f'Uh oh! {args.name} not found in {args.file}. Possible names are {sorted(list(data.keys()))}')
    exit()
model = data[args.name]
dt = 1.0/60.0

jumps = []
falls = []


for duration in np.arange(model['minHoldDuration'],model['maxHoldDuration'],(model['maxHoldDuration']-model['minHoldDuration'])/(args.num-1)-0.00000000001):

    ys = []
    y = 0
    ts = []
    t = 0
    jump = []
    jumps.append(jump)
    fall = []
    falls.append(fall)
    if  model['up-control_reset'] != 'None':
        vy = model['up-control_reset']
        for _ in np.arange(0,duration,dt):
            ys.append(y)
            ts.append(t)
            t += dt
            y -= vy*dt
            vy += model['up-control_gravity']*dt
            jump.append(y)
        descent = False
        vy = model['up-fixed_reset']+vy*model['up-fixed_mult']
        current = jump
    else:
        vy = model['up-fixed_reset']
        current = jump

    while y > args.floor*args.tilesize:
        ys.append(y)
        ts.append(t)
        if vy >= 0.0 and not descent:
            descent = True
            #vy = model['down_reset']+vy*model['down_mult']
            current = fall
        t += dt
        y -= vy*dt
        current.append(y)
        if descent or model['up-fixed_gravity'] == 0.0:
            vy += model['down_gravity']*dt
        else:
            vy += model['up-fixed_gravity']*dt

jumps = [np.round(np.array(jump)/args.tilesize) for jump in jumps]
falls = [np.round(np.array(jump)/args.tilesize) for jump in falls]

merged_jumps = np.vstack([j.reshape(-1,1) for j in jumps])
merged_jumps_t = np.vstack([np.array(range(len(j))).reshape(-1,1) for j in jumps])*args.tilesize*args.speed/60.0/60.0


merged_jumps_x = np.round(merged_jumps_t/args.tilesize)



tile_arc = [(0,0)]
tile_arcs = [tile_arc]
for x,y in zip(merged_jumps_x,merged_jumps):
    pos = (int(x),int(-y))
    if pos == (0,0) and tile_arc[-1] != (0,0):
        tile_arc = [(0,0)]
        tile_arcs.append(tile_arc)
    if pos != tile_arc[-1]:
        tile_arc.append(pos)

merged_falls = np.vstack([j.reshape(-1,1) for j in falls])
merged_falls_t = np.vstack([np.array(range(len(j))).reshape(-1,1) for j in falls])*16.0*10.0/60.0/60.0
merged_falls_x = np.round(np.array(merged_falls_t)/args.tilesize)



fall_arcs = []
origin = (int(merged_falls_x[0]),-int(merged_falls[0]))
prev_y = float('inf')
for x,y in zip(merged_falls_x,merged_falls):
    pos = (int(x),-int(y))

    if pos[1] < prev_y:
        fall_arc = [(0,0)]
        origin = pos
        fall_arcs.append(fall_arc)
    prev_y = pos[1]
    pos_offset = (int(x)-origin[0],-int(y)-origin[1])
    if pos_offset != fall_arc[-1]:
        fall_arc.append(pos_offset)

import itertools


output = []
for (jump,fall) in itertools.product(tile_arcs,fall_arcs):
    fall = [(f[0]+jump[-1][0],f[1]+jump[-1][1]) for f in fall]
    if fall[-1][1] < 0:
        continue
    else:
        output.append(('[\n\t'+',\n\t'.join([str(list(p)) for p in jump[1:]+fall])+'\n]'))

print('['+ ',\n'.join(output) + ']')
