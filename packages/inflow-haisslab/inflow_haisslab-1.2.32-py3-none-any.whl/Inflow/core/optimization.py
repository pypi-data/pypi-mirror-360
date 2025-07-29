# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 14:55:01 2023

@author: tjostmou
"""
import logging, time
import multiprocessing
from functools import wraps


def terminate_all_jobs():
    for child in multiprocessing.active_children():
        child.terminate()


class JobContext:
    def __init__(self, termination_time=5):
        self.termination_time = termination_time

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger("optmimisation")
        logger.info(f"Clearing out any remaining subprocess from RAM. Waiting {self.termination_time} seconds")
        time.sleep(self.termination_time)
        try:
            terminate_all_jobs()
        except Exception:
            logger.warning(
                "Could not clear some processes. May lead to problems in the data."
                "Be carrefull. May stop and relaunch for safety."
            )
        time.sleep(self.termination_time)


def job_context_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get("job_termination", False):
            return func(*args, **kwargs)
        with JobContext(kwargs.get("job_wait_time", 2.5)):
            return func(*args, **kwargs)

    return wrapper
