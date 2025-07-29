import numpy as np
import h5py

def hdf5_read(path):

    dict = load_dict_from_hdf5(path)

    return(dict)


def load_dict_from_hdf5(filename):
    """
    ....
    """
    h5file =  h5py.File(filename, 'r', locking = False) 
    return recursively_load_dict_contents_from_group(h5file, '/')
def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans