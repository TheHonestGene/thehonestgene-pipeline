from celery.utils.log import get_task_logger
from thehonestgenepipeline.celery import celery
from imputor.core import impute as imp  
from os import path
import h5py
from . import GENOTYPE_FOLDER
from . import DATA_FOLDER
import logging

logger = get_task_logger(__name__)


@celery.task(serialiazer='json')
def convert(filename):
    try:
        logger.info('Starting Conversion')
        genotype_file= '%s/ORIGINAL/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = _get_platform_from_genotype(genotype_file)
        nt_map_file = '%s/%s_nt_map.pickled' % (DATA_FOLDER,version)
        result = imp.convert_genotype_nt_key_encoding(genotype_file,output_file,nt_map_file)
        logger.info('Finished Conversion')
    except Exception as err:
        raise err
    return result
    
@celery.task(serialiazer='json')
def impute(filename):
    try:
        logger.info('Starting Imputation')
        genotype_file= '%s/CONVERTED/%s' % (GENOTYPE_FOLDER,filename)
        output_file = '%s/IMPUTED/%s' % (GENOTYPE_FOLDER,filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in 
        version = '23andme_v1'
        ld_folder = '%s/LD_DATA/%s' % (DATA_FOLDER,version)
        result = imp.impute(genotype_file,ld_folder,output_file)
        logger.info('Finished Imputation')
    except Exception as err:
        raise err
    return result


@celery.task(serialiazer='json')
def imputation(filename):
    result = {}
    logger.info('Starting Imputation Pipeline')
    result['convert'] = convert(filename)
    result['imputation'] = impute(filename)
    logger.info('Finished Imputation Pipeline')
    return result


def _get_platform_from_genotype(filename):
    return '23andme_v1'