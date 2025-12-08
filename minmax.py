'''
Browse training dataset and find min and max values for all input parameters.
Outputs a .txt file with the min and max values.
'''

import numpy as np
import pandas as pd
import os

DIRS = ['/STER/hydroModels/camille/phantom/macetraining/3d/v17-5-1k/chem_output/']
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
outputfile = os.path.join(SOURCE_DIR,'data', 'minmax.txt')

files = []

# headers to skip
skip = {'radius(AU)', 'mu'}
# headers to keep (ignoring abundances and time, they'll be treated separately)
keep = {'# time','n(cm-3)','T(K)', 'A_UV', 'xi'}

# abundance cutoff
abundance_cutoff = 1e-20
# precision cutoff
precision_cutoff = 1e-40

print('- Searching for .chem files in:')
for DIR in DIRS:
    print(f'        - {DIR}')
    files += [os.path.join(DIR,f) for f in sorted(os.listdir(DIR)) if f.endswith('.chem')]
    print(f'            -> Found {len(files)} files')

mins = {}
maxs = {}   
print('- Computing min and max values for all parameters...')
for fi,i in zip(files, range(len(files))):
    data = pd.read_csv(fi, sep='\s+\s+', engine='python')
    print(f'        - Processing file: {i}/{len(files)}')
    abs = []
    for key in data.keys():
        if key in skip:
            data = data.drop(columns=key)
        elif key in keep:
            if i == 0: 
                mins[key] = data[key].min()
                maxs[key] = data[key].max()
            else:
                mins[key] = np.minimum(mins[key], data[key].min())
                maxs[key] = np.maximum(maxs[key], data[key].max())
        elif key == '# time(s)':
            timestep = [b-a for a,b in zip(data[key][:-1], data[key][1:])]
            if i == 0:
                mins['time'] = min(timestep)
                maxs['time'] = max(timestep)
            else:
                mins['time'] = min(mins['time'], min(timestep))
                maxs['time'] = max(maxs['time'], max(timestep))
        else:
            # abundances, concatenate all values before querying min and max
            abs += list(data[key].values)
    mins['abs'] = max(np.min(abs), abundance_cutoff)
    maxs['abs'] = np.max(abs)

           
print('- min and max values:')
print(maxs)
print(mins)

with open(outputfile, 'w') as f:
    f.write(f'rho_min: {mins["n(cm-3)"]}\n')
    f.write(f'rho_max: {maxs["n(cm-3)"]}\n')
    f.write(f'T_min: {mins["T(K)"]}\n')
    f.write(f'T_max: {maxs["T(K)"]}\n')
    f.write(f'delta_min: {mins["xi"]}\n')
    f.write(f'delta_max: {maxs["xi"]}\n')
    f.write(f'A_UV_min: {mins["A_UV"]}\n')
    f.write(f'A_UV_max: {maxs["A_UV"]}\n')
    f.write(f'n_min: {mins["abs"]}\n')
    f.write(f'n_max: {maxs["abs"]}\n')
    f.write(f'dt_max: {maxs["time"]}\n')
