from __future__ import absolute_import
from celery import Celery
import os

os.environ.setdefault('CELERY_CONFIG_MODULE', 'thehonestgenepipeline.celeryconfig')
celery = Celery('thehonestgenepipeline',
    include=['thehonestgenepipeline.imputation','thehonestgenepipeline.ancestry','thehonestgenepipeline.riskprediction'])

celery.config_from_envvar('CELERY_CONFIG_MODULE')



if __name__ == '__main__':
    celery.start()


