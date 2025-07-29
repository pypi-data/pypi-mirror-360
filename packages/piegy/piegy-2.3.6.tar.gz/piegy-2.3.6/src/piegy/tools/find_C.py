'''
This module is used to find the C core
'''

import os


def find_C():
    C_core_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'C_core')
    C_list = os.listdir(C_core_path)
    for file in C_list:
        if file[-3:] == '.so':
            return C_core_path + '/' + file
        if file[-4:] == '.pyd':
            return C_core_path + '/' + file

    raise FileNotFoundError('C computation core not found. You can either compile manully or use the Python core instead. Please see docs.')
