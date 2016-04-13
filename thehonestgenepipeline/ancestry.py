from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from ancestor.core import ancestry as an  
from os import path
from . import GENOTYPE_FOLDER,DATA_FOLDER
from . import get_platform_from_genotype
from .progress_logger import CeleryProgressLogHandler 
import h5py

import logging

logger = get_task_logger(an.__name__)
# pass through environment

@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    progress_handler = CeleryProgressLogHandler(celery,'ancestry')
    logger.addHandler(progress_handler)

@celery.task(serialiazer='json')
def analysis(id,region):
    try:
        log_extra={'progress':5,'id':id}
        logger.info('Starting Ancestry',extra={'progress':0,'id':id})
        genotype_file= '%s/IMPUTED/%s.hdf5' % (GENOTYPE_FOLDER,id)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        platform = get_platform_from_genotype(genotype_file)
        weights_file = '%s/AN_DATA/%s_weights.hdf5' % (DATA_FOLDER,region)
        pcs_file = '%s/AN_DATA/hapmap_%s_%s_pcs.hdf5' % (DATA_FOLDER,platform,region)
        ancestry_dict = an.ancestry_analysis(genotype_file,weights_file,pcs_file,log_extra=log_extra)
        result = {'pc1':float(ancestry_dict['pc1']),'pc2':float(ancestry_dict['pc2']),'is_in_population':bool(ancestry_dict['is_in_population']),
                 'pop_mean':ancestry_dict['pop_mean'].tolist(),'pop_std':ancestry_dict['pop_std'].tolist(),'ind_lim':ancestry_dict['ind_lim'].tolist(),'population':ancestry_dict['population']}
        logger.info('Finished Ancestry',extra={'progress':100,'id':id,'state':'FINISHED'})
    except Exception as err:
        logger.error('Error during ancestry analysis',extra=log_extra)
        raise err
    return result
