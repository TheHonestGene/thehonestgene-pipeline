from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from ancestor.core import ancestry as an
from os import path
from . import GENOTYPE_FOLDER,DATA_FOLDER
from . import get_platform_from_genotype, save_analysis_data
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
def analysis(id,region,check_population):
    try:
        log_extra={'progress':5,'id':id}
        logger.info('Starting Ancestry',extra={'progress':0,'id':id})
        genotype_file= '%s/IMPUTED/%s.hdf5' % (GENOTYPE_FOLDER,id)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        platform = get_platform_from_genotype(genotype_file)
        weights_file = '%s/AN_DATA/%s_weights.hdf5' % (DATA_FOLDER,region)
        pcs_file = '%s/AN_DATA/1k_%s_%s_pcs.hdf5' % (DATA_FOLDER,platform,region)
        ancestry_dict = an.ancestry_analysis(genotype_file,weights_file,pcs_file,check_population=check_population,log_extra=log_extra)
        admixture_dict = ancestry_dict['admixture']
        result = {'indiv_pcs':ancestry_dict['indiv_pcs'].tolist(),'admixture':{
            'unadjusted_admixture':admixture_dict['unadjusted_admixture'].tolist(),
            'admixture':admixture_dict['admixture'].tolist(),
            'confidence':admixture_dict['confidence'],
            'confidence_score':float(admixture_dict['confidence_score'])
        }}
        if isinstance(ancestry_dict['check_population'],dict):
            check_pop = ancestry_dict['check_population']
            result['check_population'] = {'check_pop':check_pop['check_pop'],
            'is_in_population':bool(check_pop['is_in_population']),
            'ref_pop_std':check_pop['ref_pop_std'].tolist(),
            'ref_pop_mean_pcs':check_pop['ref_pop_mean_pcs'].tolist()}
        else:
            result['check_population'] = ancestry_dict['check_population']
        save_analysis_data(genotype_file, result, 'ancestry_%s' % region)
        logger.info('Finished Ancestry',extra={'progress':100,'id':id,'state':'FINISHED'})
    except Exception as err:
        logger.error('Error during ancestry analysis',extra=log_extra)
        raise err
    return result
