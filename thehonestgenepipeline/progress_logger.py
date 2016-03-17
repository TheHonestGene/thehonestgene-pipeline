import logging,os
import pika
import json

class CeleryProgressLogHandler(logging.StreamHandler):

    def __init__(self,BROKER,analysis_type):
        self.BROKER = BROKER
        self.analysis_type = analysis_type
        self._connect()
        logging.StreamHandler.__init__(self)
    
    def emit(self,record):
        if 'progress' in record.__dict__ and 'id' in record.__dict__:
            id = record.__dict__['id']
            queue = 'updates_%s' % id
            try:
                self._declare_queue(queue)
                progress = record.__dict__['progress']
                msg = self.format(record)
                if 'task' in record.__dict__:
                    msg = record.__dict__['task']
                state = record.__dict__.get('state','RUNNING')
                body = {'progress':progress,'task':msg,'state':state,'analysisType':self.analysis_type}
                self.channel.basic_publish(exchange='',routing_key=queue,body=json.dumps(body))
            except Exception as err:
                pass
     
    def _connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.BROKER))
        self.channel = self.connection.channel()
         
    def _declare_queue(self,queue,num_tries = 0):
       try: 
           self.channel.queue_declare(queue=queue,durable=True)
       except Exception:
           if self.connection.is_closed and num_tries < 3:
               self._connect()
               self._declare_queue(queue,num_tries = num_tries+1)
