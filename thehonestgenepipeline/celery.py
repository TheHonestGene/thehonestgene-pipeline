from __future__ import absolute_import
from celery import Celery

celery = Celery('thehonestgenepipeline',
    include=['thehonestgenepipeline.imputation','thehonestgenepipeline.ancestry'])
celery.config_from_object('celeryconfig')


if __name__ == '__main__':
    celery.start()


