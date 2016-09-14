"""
Pipeline for imputation
"""
from os import path
from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from imputor.core import impute as imp
from . import GENOTYPE_FOLDER, DATA_FOLDER
from . import get_platform_from_genotype, save_analysis_data
from .progress_logger import CeleryProgressLogHandler



LOGGER = get_task_logger(imp.__name__)


@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    """
    Log messages back to broker
    """
    progress_handler = CeleryProgressLogHandler(celery, 'imputation')
    LOGGER.addHandler(progress_handler)

@celery.task(serialiazer='json')
def convert(genotype_id, log_extra=None):
    """
    Convert nucleotides to binary encoding
    """
    if log_extra is None:
        log_extra = {'progress':0, 'max_progress':100}
    try:
        log_extra['id'] = genotype_id
        filename = '%s.hdf5' % genotype_id
        LOGGER.info('Starting Conversion', extra=log_extra)
        genotype_file = '%s/ORIGINAL/%s' % (GENOTYPE_FOLDER, filename)
        output_file = '%s/CONVERTED/%s' % (GENOTYPE_FOLDER, filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in
        platform = get_platform_from_genotype(genotype_file)
        nt_map_file = '%s/NT_DATA/%s_nt_map.pickled' % (DATA_FOLDER, platform)
        result = imp.convert_genotype_nt_key_encoding(genotype_file, output_file, nt_map_file, log_extra=log_extra)
        save_analysis_data(output_file, result, 'convert')
        LOGGER.info('Finished Conversion', extra={'progress':log_extra.get('max_progress', 100), 'id':genotype_id})
    except Exception as err:
        LOGGER.error('Error during conversion', extra=log_extra)
        raise err
    return result

@celery.task(serialiazer='json')
def impute(genotype_id, log_extra=None):
    """
    Impute missing SNPs
    """
    if log_extra is None:
        log_extra = {'progress':0, 'max_progress':100}
    try:
        log_extra['id'] = genotype_id
        filename = '%s.hdf5' % genotype_id
        LOGGER.info('Starting Imputation', extra=log_extra)
        genotype_file = '%s/CONVERTED/%s' % (GENOTYPE_FOLDER, filename)
        output_file = '%s/IMPUTED/%s' % (GENOTYPE_FOLDER, filename)
        if not path.exists(genotype_file):
            raise Exception('Genotype file %s not found' % genotype_file)
        # Need to pass in
        platform = get_platform_from_genotype(genotype_file)
        ld_folder = '%s/LD_DATA/%s' % (DATA_FOLDER, platform)
        result = imp.impute(genotype_file, ld_folder, output_file, log_extra=log_extra)
        save_analysis_data(output_file, result, 'imputation')
        LOGGER.info('Finished Imputation', extra={'progress':log_extra.get('max_progress', 100), 'id':genotype_id})
    except Exception as err:
        LOGGER.error('Error during imputation', extra=log_extra)
        raise err
    return result


@celery.task(serialiazer='json')
def imputation(genotype_id):
    """
    Entire imputation pipeline consisting of convert and impute
    """
    result = {}
    LOGGER.info('Starting Imputation Pipeline', extra={'progress':0, 'id':genotype_id})
    result['convert'] = convert(genotype_id, {'progress':5, 'max_progress':20})
    result['imputation'] = impute(genotype_id, {'progress':20, 'max_progress':95})
    LOGGER.info('Finished Imputation Pipeline', extra={'progress':100, 'id':genotype_id, 'state':'FINISHED'})
    return result
