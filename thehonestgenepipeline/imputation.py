from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from imputor.core import impute as imp  
from os import path
import h5py
from . import GENOTYPE_FOLDER,DATA_FOLDER
from .progress_logger import CeleryProgressLogHandler 
import logging

logger = get_task_logger(__name__)


@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    progress_handler = CeleryProgressLogHandler(celery.conf.BROKER_URL)
    logger.addHandler(progress_handler)

@celery.task(serialiazer='json')
def convert(id):
    try:
        filename = '%s.hdf5' % id
        logger.info('Starting Conversion',extra={'progress':5,'id':id})
        genotype_file= '%s/ORIGINAL/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = _get_platform_from_genotype(genotype_file)
        nt_map_file = '%s/%s_nt_map.pickled' % (DATA_FOLDER,version)
        result = imp.convert_genotype_nt_key_encoding(genotype_file,output_file,nt_map_file)
        logger.info('Finished Conversion',extra={'progress':20,'id':id})
    except Exception as err:
        raise err
    return result
    
@celery.task(serialiazer='json')
def impute(id):
    try:
        filename = '%s.hdf5' % id
        logger.info('Starting Imputation',extra={'progress':25,'id':id})
        genotype_file= '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/IMPUTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = '23andme_v1'
        ld_folder = '%s/LD_DATA/%s' % (DATA_FOLDER,version)
        result = imp.impute(genotype_file,ld_folder,output_file)
        logger.info('Finished Imputation',extra={'progress':95,'id':id})
    except Exception as err:
        raise err
    return result


@celery.task(serialiazer='json')
def imputation(id):
    result = {}
    logger.info('Starting Imputation Pipeline',extra={'progress':0,'id':id})
    result['convert'] = convert(id)
    result['imputation'] = impute(id)
    logger.info('Finished Imputation Pipeline',extra={'progress':100,'id':id})
    return result


@celery.task(serialiazer='json')
def test():
    #logger.addHandler(progress_handler)
    logger.info('start test')
    logger.info('log test no celery event',extra={'some data':'test'})
    logger.info('log test celery event',extra={'progress':50,'id':'someid'})
    logger.info('log test celery event and custom text',extra={'progress':80,'task':'text','id':'someid2'})
    import time
    time.sleep(5)
    #logger.removeHandler(fh);
    return  {'status':'OK'}

def _get_platform_from_genotype(filename):
    return '23andme_v1'