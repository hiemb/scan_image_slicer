#!/usr/bin/env python3

import os
import sys
import logging
import logging.handlers

LOGGING_LEVEL = logging.INFO

def listener_configurer(p):
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(p.log_path, mode='w')
    stream_formatter = logging.Formatter(":: " + "%(message)s")

    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] - %(message)s",
        datefmt="%d %b %Y %a %I:%M:%S %p"
    )

    stream_handler.setFormatter(stream_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

def listener_process(p, queue, configurer):
    configurer(p)
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, trackeback
            print("Logger error: ", file=sys.stderr)
            trackeback.print_exc(file=sys.stderr)

def queue_configurer(queue):
    queue_handler = logging.handlers.QueueHandler(queue)
    logger = logging.getLogger()

    if not logger.handlers:
        logger.addHandler(queue_handler)

    logger.setLevel(LOGGING_LEVEL)

    return logger

def worker_configurer(queue):
    queue_handler = logging.handlers.QueueHandler(queue)
    logger = logging.getLogger()
    logger.addHandler(queue_handler)
    logger.setLevel(LOGGING_LEVEL)