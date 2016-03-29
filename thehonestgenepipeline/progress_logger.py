import logging,os
import pika
import json


class ProgressLogger:

    def __init__(self,BROKER,analysis_type,id,logger,data=None):
        self.BROKER = BROKER
        self.logger = logger
        self.data = data
        self.analysis_type = analysis_type
        self.id = id
        self.queue = 'updates_%s' % id
        self.progress = 0
        self._setup()


        
    def log(self,task,progress=None,state='RUNNING',data=None):
        if progress is not None:
            self.progress=progress
        try:
            if self.logger:
                self.logger.info(task)
            if data == None:
                data = self.data
            body = {'progress':self.progress,'task':task,'state':state,'analysisType':self.analysis_type,'data':data, 'id':self.id} 
            self.channel.basic_publish(exchange='',routing_key=self.queue,body=json.dumps(body))
        except Exception as err:
            pass
        
    def _setup(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.BROKER))
        self.channel = self.connection.channel()
               

class CeleryProgressLogHandler(logging.StreamHandler):

    def __init__(self,BROKER,analysis_type):
        self.BROKER = BROKER
        self.analysis_type = analysis_type
        self.channel = None
        self._connect()
        print('connected')
        logging.StreamHandler.__init__(self)
    
    def emit(self,record):
        if 'progress' in record.__dict__ and 'id' in record.__dict__:
            self._connect()
            id = record.__dict__['id']
            queue = 'updates_%s' % id
            try:
                progress = record.__dict__['progress']
                msg = self.format(record)
                if 'task' in record.__dict__:
                    msg = record.__dict__['task']
                state = record.__dict__.get('state','RUNNING')
                additional_data =  record.__dict__.get('data',None)
                body = {'progress':progress,'task':msg,'state':state,'analysisType':self.analysis_type,'data':additional_data,'id': id}
                self.channel.basic_publish(exchange='',routing_key=queue,body=json.dumps(body))
            except Exception as err:
                print(err)
                pass
     
    def _connect(self):
        if not self.channel or self.channel.connection.is_open == False or self.channel.is_open == False:
            print('Connect')
            self.channel = pika.BlockingConnection(pika.ConnectionParameters(self.BROKER)).channel()
