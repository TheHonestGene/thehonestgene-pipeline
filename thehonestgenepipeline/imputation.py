from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from imputor.core import impute as imp  
from os import path
import h5py
from . import GENOTYPE_FOLDER,DATA_FOLDER
from .progress_logger import CeleryProgressLogHandler 
import logging

logger = get_task_logger(imp.__name__)


@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    progress_handler = CeleryProgressLogHandler(celery,'imputation')
    logger.addHandler(progress_handler)

@celery.task(serialiazer='json')
def convert(id,log_extra={'progress':0,'max_progress':100}):
    try:
        log_extra['id'] = id
        filename = '%s.hdf5' % id
        logger.info('Starting Conversion',extra=log_extra)
        genotype_file= '%s/ORIGINAL/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = _get_platform_from_genotype(genotype_file)
        nt_map_file = '%s/%s_nt_map.pickled' % (DATA_FOLDER,version)
        result = imp.convert_genotype_nt_key_encoding(genotype_file,output_file,nt_map_file,log_extra=log_extra)
        logger.info('Finished Conversion',extra={'progress':log_extra.get('max_progress',100),'id':id})
    except Exception as err:
        logger.error('Error during conversion',extra={'state':'ERROR','id':id})
        raise err
    return result
    
@celery.task(serialiazer='json')
def impute(id,log_extra={'progress':0,'max_progress':100}):
    try:
        log_extra['id'] = id
        filename = '%s.hdf5' % id
        logger.info('Starting Imputation',extra=log_extra)
        genotype_file= '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/IMPUTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = '23andme_v1'
        ld_folder = '%s/LD_DATA/%s' % (DATA_FOLDER,version)
        result = imp.impute(genotype_file,ld_folder,output_file,log_extra=log_extra)
        logger.info('Finished Imputation',extra={'progress':log_extra.get('max_progress',100),'id':id})
    except Exception as err:
        logger.error('Error during imputation',extra={'state':'ERROR','id':id})
        raise err
    return result


@celery.task(serialiazer='json')
def imputation(id):
    result = {}
    logger.info('Starting Imputation Pipeline',extra={'progress':0,'id':id})
    result['convert'] = convert(id,{'progress':5,'max_progress':20})
    result['imputation'] = impute(id,{'progress':20,'max_progress':95})
    logger.info('Finished Imputation Pipeline',extra={'progress':100,'id':id,'state':'FINISHED'})
    return result

def _get_platform_from_genotype(filename):
    return '23andme_v1'
