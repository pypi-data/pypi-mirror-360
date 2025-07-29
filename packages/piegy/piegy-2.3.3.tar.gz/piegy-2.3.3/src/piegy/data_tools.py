'''
Stores and reads a model object.

Functions:
- save_data:    save a model object.
- read_data:    read a model object.
'''


from . import simulation

import json
import gzip
import os


def save_data(mod, dirs = '', print_msg = True):
    '''
    Saves a model object. Data will be stored at dirs/data.json.gz

    Inputs:
    - mod:        Your model object.
    - dirs:       Where to save it.
    - print_msg:  Whether to print message after saving.
    '''

    try:
        _ = mod.N
    except AttributeError:
        raise ValueError('mod is not a model object')

    if dirs != '':
        # add slash '/'
        if dirs[:-1] != '/':
            dirs += '/'
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        
    data = []
    
    inputs = []
    inputs.append(mod.N)
    inputs.append(mod.M)
    inputs.append(mod.maxtime)
    inputs.append(mod.record_itv)
    inputs.append(mod.sim_time)
    inputs.append(mod.boundary)
    inputs.append(mod.I.tolist())
    inputs.append(mod.X.tolist())
    inputs.append(mod.P.tolist())
    inputs.append(mod.print_pct)
    inputs.append(mod.seed)
    inputs.append(mod.check_overflow)
    data.append(inputs)

    # skipped rng
    
    outputs = []
    outputs.append(mod.max_record)
    outputs.append(mod.compress_itv)
    outputs.append(mod.U.tolist())
    outputs.append(mod.V.tolist())
    outputs.append(mod.Upi.tolist())
    outputs.append(mod.Vpi.tolist())
    # H&Vpi_total are not saved, will be calculated when reading the data
    data.append(outputs)
    
    data_json = json.dumps(data)
    data_bytes = data_json.encode('utf-8')
    data_dirs = dirs + 'data.json.gz'
    
    with gzip.open(data_dirs, 'w') as f:
        f.write(data_bytes)
    
    if print_msg:
        print('data saved: ' + data_dirs)



def read_data(dirs):
    '''
    Reads and returns a model object.

    Inputs:
    - dirs:       where to read from, just provide the folder-subfolder names. Don't include 'data.json.gz'
    - print_msg:  this function prints a message when the mod.compress_itv != None. Setting print_msg = False will skip ignore this message.

    Returns:
    - mod: a piegy.model.model object read from the data.
    '''
    
    if dirs != '':
        # add slash '/'
        if dirs[:-1] != '/':
            dirs += '/'
        if not os.path.exists(dirs):
            raise FileNotFoundError('dirs not found: ' + dirs)
            
    if not os.path.isfile(dirs + 'data.json.gz'):
        raise FileNotFoundError('data not found in ' + dirs)
    
    with gzip.open(dirs + 'data.json.gz', 'r') as f:
        data_bytes = f.read()
    data_json = data_bytes.decode('utf-8')
    data = json.loads(data_json)

    # inputs
    try:
        mod = simulation.model(N = data[0][0], M = data[0][1], maxtime = data[0][2], record_itv = data[0][3],
                            sim_time = data[0][4], boundary = data[0][5], I = data[0][6], X = data[0][7], P = data[0][8], 
                            print_pct = data[0][9], seed = data[0][10], check_overflow = data[0][11])
    except:
        raise ValueError('Invalid input parameters saved in data')

    # outputs
    try:
        mod.set_data(data_empty = False, max_record = data[1][0], compress_itv = data[1][1], 
                    U = data[1][2], V = data[1][3], Upi = data[1][4], Vpi = data[1][5])
    except:
        raise ValueError('Invalid model results saved in data')
    
    return mod





