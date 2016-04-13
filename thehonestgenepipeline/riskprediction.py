from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from thehonestgenepipeline.celery import celery
from riskpredictor.core import predictor as pred  
from os import path
from . import GENOTYPE_FOLDER,DATA_FOLDER
from . import get_platform_from_genotype
from .progress_logger import CeleryProgressLogHandler

import h5py

import logging

logger = get_task_logger(pred.__name__)
# pass through environment

@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    progress_handler = CeleryProgressLogHandler(celery,'riskprediction')
    logger.addHandler(progress_handler)

@celery.task(serialiazer='json')
def run(id,trait):
    try:
        log_extra={'id':id,'progress':0,'data':trait}
        genotype_file= '%s/IMPUTED/%s.hdf5' % (GENOTYPE_FOLDER,id)
        risk = pred.predict(genotype_file,trait,log_extra=log_extra)
        result = {'trait':trait,'risk':risk}
        logger.info('Finished Risk Prediction',extra={'id':id,'progress':100,'state':'FINISHED','data':trait})
    except Exception as err:
        logger.error('Error calculating risk prediction',extra=log_extra)
        raise err
    return result