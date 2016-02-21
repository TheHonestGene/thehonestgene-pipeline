from kombu import Exchange, Queue
import os
BROKER_URL = os.environ['CELERY_BROKER']
CELERY_RESULT_BACKEND='rpc://'
CELERY_RESULT_PERSISTENT = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']


imputation_exchange = Exchange('imputation', type='direct')
ancestry_exchange = Exchange('ancestry',type='direct')
riskprediction_exchange = Exchange('riskprediction',type='direct')



CELERY_QUEUES = (
    Queue('imputation', imputation_exchange, routing_key='imputation'),
    Queue('ancestry', ancestry_exchange, routing_key='ancestry'),
    Queue('riskprediction',riskprediction_exchange,routing_key='riskprediction')
)

   
CELERY_ROUTES = {
        'thehonestgenepipeline.imputation.imputation':{'queue':'imputation'},
        'thehonestgenepipeline.imputation.convert':{'queue':'imputation'},
        'thehonestgenepipeline.imputation.impute':{'queue':'imputation'},
        'thehonestgenepipeline.ancestry.analysis':{'queue':'ancestry'},
        'thehonestgenepipeline.riskprediction.run':{'queue':'riskprediction'}
}


