"""
Common utility functions
"""

from os import environ
import json
import h5py

# pass through environment
BASE_FOLDER = environ.get('BASE_FOLDER', './')
GENOTYPE_FOLDER = environ.get('GENOTYPE_FOLDER', '/%s/GENOTYPES' % BASE_FOLDER)
DATA_FOLDER = environ.get('DATA_FOLDER', '/%s/DATA' % BASE_FOLDER)

def get_platform_from_genotype(filename):
    """
    Retrieve platform, version and source from imput file
    """
    f = h5py.File(filename, 'r')
    platform = None
    try:
        source = f.attrs['source']
        version = f.attrs['version']
        platform = source
        if version is not None and version != '':
            platform += '_%s' % version
    finally:
        f.close()
    return platform

def save_analysis_data(filename, data, key):
    """
    Save the results from the analysis in the output file
    """
    f = h5py.File(filename, 'r+')
    try:
        f.attrs[key] = json.dumps(data)
        f.flush()
    finally:
        f.close()
