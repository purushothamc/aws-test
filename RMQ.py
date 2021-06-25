import pika
import logging

class MQReader(object):
    def __init__(self,queue):
        self._channel=None
        self._queuename=queue
        self._tag=None
        self._customer_tag=None
        self.data=None

    def nonBlockingRead(self,hostname='localhost',user='guest',passwd='guest'):
        credentials = pika.PlainCredentials(username=user, password=passwd)
        self._connection =pika.BlockingConnection(
            pika.ConnectionParameters(host=hostname, credentials=credentials,
                                      socket_timeout=5, heartbeat=600,
                                      blocked_connection_timeout=300))
        self._channel = self._connection.channel()
        q=self._channel.queue_declare(queue=self._queuename,arguments={'x-expires' : 172800000})
        method_frame, properties, body = self._channel.basic_get(self._queuename)
        wasDataFound=False
        if (method_frame):
            logging.debug("Read from queue %s - %s\n"%(self._queuename,body))
            self._channel.basic_ack(method_frame.delivery_tag)
            self.data=body
            wasDataFound=True
        else:
            logging.debug("No data available to be read from queue %s - %s\n"%(self._queuename,body))
            self.data=None
        self._channel.cancel()
        self._channel.close()
        self._connection.close()
        return wasDataFound

    def clear_queue(self,hostname='localhost',user='guest',passwd='guest'):
        credentials = pika.PlainCredentials(username=user, password=passwd)
        self._connection =pika.BlockingConnection(
            pika.ConnectionParameters(host=hostname, credentials=credentials,
                                      socket_timeout=5, heartbeat=600,
                                      blocked_connection_timeout=300))
        self._channel = self._connection.channel()
        q=self._channel.queue_declare(queue=self._queuename,arguments={'x-expires' : 172800000})
        method_frame, properties, body = self._channel.basic_get(self._queuename)
        while (method_frame):
            logging.debug("Read from queue %s - %s\n"%(self._queuename,body))
            self._channel.basic_ack(method_frame.delivery_tag)
            method_frame, properties, body = self._channel.basic_get(self._queuename)
        self._channel.cancel()
        self._channel.close()
        self._connection.close()
        logging.info("Finished clearing the %s Queue"% self._queuename)

    def blockingRead(self,hostname='localhost',user='guest',passwd='guest'):
        credentials = pika.PlainCredentials(username=user, password=passwd)
        self._connection =pika.BlockingConnection(
            pika.ConnectionParameters(host=hostname,credentials=credentials,
                                      blocked_connection_timeout=300, heartbeat=600,
                                      socket_timeout=5))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._queuename,arguments={'x-expires' : 172800000})
        #self._tag=self._channel.basic_consume(self.callback,queue=self._queuename,no_ack=True)
        self._tag=self._channel.basic_consume(self.callback,queue=self._queuename)
        #print(' [*] Waiting for messages. To exit press CTRL+C')
        self._channel.start_consuming()
        return True

    def callback(self,ch, method, properties, body):
        self.data=body
        self._channel.basic_ack(method.delivery_tag)
        # Shut Down after reading
        self._channel.close()
def sendData(queuename,item,hostname='localhost',user='guest',passwd='guest'):
    credentials = pika.PlainCredentials(username=user, password=passwd)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=hostname, credentials=credentials,
                                  socket_timeout=5, connection_attempts=3,
                                  heartbeat=600, blocked_connection_timeout=300,
                                  retry_delay=3))
    channel = connection.channel()
    channel.queue_declare(queue=queuename,arguments={'x-expires' : 172800000})
    channel.basic_publish(exchange='',routing_key=queuename,body=item)
    logging.debug("Sent %s to %s"%(item,queuename))
    connection.close()
def sendDataDurable(queuename,item,hostname='localhost',user='guest',passwd='guest'):
    credentials = pika.PlainCredentials(username=user, password=passwd)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=hostname, credentials=credentials,
                                  socket_timeout=5, connection_attempts=3,
                                  heartbeat=600, blocked_connection_timeout=300,
                                  retry_delay=3))
    channel = connection.channel()
    channel.queue_declare(queue=queuename,durable=True)
    channel.basic_publish(exchange='',routing_key=queuename,body=item)
    logging.debug("Sent %s to %s"%(item,queuename))
    connection.close()

# vim: tabstop=4 expandtab shiftwidth=2 softtabstop=2
