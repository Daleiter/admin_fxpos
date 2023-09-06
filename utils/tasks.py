# tasks.py
from models.tiket_model import create_help_desk_tiket
from flask import  current_app
import multiprocessing
import time
from redis import Redis
from rq import get_current_job

def update_progress(progress):
    job = get_current_job()
    job.meta['progress'] = progress
    job.save_meta()

def update_status(status):
    job = get_current_job()
    job.meta['status'] = status
    job.save_meta()

def my_background_task(incedent):
    with current_app.app_context():
        update_status("started")
        print("startted task")
        create_help_desk_tiket(incedent)
    

    # Task completed; set the progress to 100% and store it
    update_progress(100)
    update_status("finished")
