#!/usr/bin/python
from multiprocessing import Process, Queue, freeze_support, Lock
from os.path import splitext, basename

# from celery.task.base import task
import threading
import time
import logging
import pickle
import RMQ
import argparse
import socket
import os
import subprocess
import json
import os.path
import logging.handlers


def worker(taskSpec):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    if 'fjson' in taskSpec:
        dataVal = {"Status": "", "Value": ""}

        # check whether we can access the wr json file in given directory.
        # this would be in-accessible when WR shared area is not mounted on machine.

        # Successful validation, start WR in WRE.
        genWRID(taskSpec)
        dataVal["Status"] = "Pass"


def genWRID(taskSpec):
    # Create a WRE process for running the Work Request.
    work_request = taskSpec["fjson"]
    work_request = json.loads(work_request)
    print(work_request)

    # delete_artifact(file_name, ArtifactType.staging.
    #psgen = subprocess.Popen([r'python', 'WRE.py', '--WRID', WRID],
    #                         cwd='../components/wre/', shell=False, stdout=f, stderr=f)

    # If we're unable to create WRE process, we reject the WR.
    #if psgen.returncode is not None and psgen.returncode < 0:
    #    logging.error("WRV Rejected the Work Request")

class JobEventLoop(threading.Thread):
    def __init__(self, hostname, channelPrefix):
        super(JobEventLoop, self).__init__()
        self._stop = threading.Event()
        self._stop.clear()
        self._jobQueueName = "%s.WRVSubmitQueue" % channelPrefix
        self._doneQueueName = "%s.WRVDoneQueue" % channelPrefix
        # self.clear_queue=True
        self._hostname = hostname

    def run(self):
        incomingJobMQ = RMQ.MQReader(self._jobQueueName)
        # This queue will be cleared during the te launched loop
        # if self.clear_queue:
        #   incomingJobMQ.clear_queue(self._hostname,'guest','guest')

        jobDoneMQ = RMQ.MQReader(self._doneQueueName)
        jobDoneMQ.clear_queue(self._hostname, 'guest', 'guest')
        while not self.stopped():
            incomingJobMQ.blockingRead(self._hostname, 'guest', 'guest')
            jobDoneMQ.clear_queue(self._hostname, 'guest', 'guest')
            taskSpec = (pickle.loads(incomingJobMQ.data))
            # logging.info(taskSpec)
            lock = Lock()
            logging.info(taskSpec)
            p = Process(target=worker, args=(taskSpec,))
            p.start()
            p.join()
            logging.info("Finished job!")

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


def main():
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.debug("Starting up")

    channelPrefix = str(socket.gethostname()).lower()
    # Send a "I am Alive" message that signals we are starting up (used for atleast reboot detection)
    #  However, we need to wait for the RabbitMQ (erlang) service to boot up which may take some time
    logging.info("Trying to posted alive status (maybe take a few retries)")
    launchQueue = "te.launched"
    while True:
        try:
            tmpQueue = RMQ.MQReader("%s.WRVSubmitQueue" % channelPrefix)
            tmpQueue.clear_queue('localhost', 'guest', 'guest')
            teLaunchMQ = RMQ.MQReader(launchQueue)
            teLaunchMQ.clear_queue('localhost', 'guest', 'guest')
            RMQ.sendData(launchQueue, pickle.dumps("IAmAlive"), 'localhost', 'guest', 'guest')
            break
        except Exception as e:
            time.sleep(15)
    logging.info("Posted alive status to %s" % launchQueue)

    parser = argparse.ArgumentParser()
    parser.add_argument("--clienthost", type=str, default='localhost')
    args = parser.parse_args()
    clientHost = str(args.clienthost).lower()
    jobEventLoop = JobEventLoop(clientHost, channelPrefix)
    jobEventLoop.daemon = True
    lock = Lock()
    jobEventLoop.start()
    while True:
        time.sleep(5)
    jobEventLoop.join()
    logging.debug("Shutting down")


if __name__ == '__main__':
    main()

# vim: tabstop=4 expandtab shiftwidth=2 softtabstop=2
