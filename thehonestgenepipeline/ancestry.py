from celery.utils.log import get_task_logger
from thehonestgenepipeline.celery import celery
from ancestor.core import ancestry as an  
from os import path
from . import GENOTYPE_FOLDER
from . import DATA_FOLDER
import h5py

import logging

logger = get_task_logger(__name__)
# pass through environment

@celery.task(serialiazer='json')
def analysis(genotype,weights_file,pcs_file):
    try:
        logger.info('Starting Ancestry')
        genotype_file= '%s/IMPUTED/%s' % (GENOTYPE_FOLDER,genotype)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = '23andme_v1'
        weights_file = '%s/%s' % (DATA_FOLDER,weights_file)
        pcs_file = '%s/%s' % (DATA_FOLDER,pcs_file)
        ancestry_dict = an.ancestry_analysis(genotype_file,weights_file,pcs_file)
        result = {'pc1':float(ancestry_dict['pc1']),'pc2':float(ancestry_dict['pc2']),'is_in_population':bool(ancestry_dict['is_in_population']),
                 'pop_mean':ancestry_dict['pop_mean'].tolist(),'pop_std':ancestry_dict['pop_std'].tolist(),'ind_lim':ancestry_dict['ind_lim'].tolist(),'population':ancestry_dict['population']}
        logger.info('Finished Ancestry')
    except Exception as err:
        raise err
    return result
   


def _get_platform_from_genotype(h5f):
    return '23andme_v1'