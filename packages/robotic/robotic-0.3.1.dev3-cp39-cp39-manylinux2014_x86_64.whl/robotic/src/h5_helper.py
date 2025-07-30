#!/usr/bin/env python3

import argparse
import h5py

class H5Writer:
    def __init__(self, filename):
        self.fil = h5py.File(filename, 'w')

    def write(self, name, data, dtype = 'float32'):
        self.fil.create_dataset(name, data=data, dtype=dtype)

class H5Reader:
    def __init__(self, filename):
        self.fil = h5py.File(filename, 'r')

    def print_attrs(self,name, obj):
        if isinstance(obj, h5py.Dataset):
            print('   ', name, obj.name, obj.shape, obj.dtype, f'{obj.size*obj.dtype.itemsize/1024:.2f}kB')
            if obj.dtype=='int8':
                print('       ', ''.join([chr(x) for x in obj[()]]))
            elif obj.size<20:
                print('       ', obj[()])
        else:
            print('---', name)

    def print_info(self):
        self.fil.visititems(self.print_attrs)

    def read(self, name):
        return self.fil[name][()]
