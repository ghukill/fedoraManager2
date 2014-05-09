from fedoraManager2 import app
from fedoraManager2 import models
from fedoraManager2.actions import actions

# flask proper
from flask import render_template, request, session

# forms
from flask_wtf import Form
from wtforms import TextField

import time
import json
import pickle

# get celery instance / handle
from cl.cl import celery
import jobs
import forms
from redisHandles import *

# fake session data
####################################
# set the secret key
app.secret_key = 'ShoppingHorse'
####################################

	

@app.route("/quickAdd/<task_num>")
def quickAdd(task_num):
	print "Starting request..."
	
	count = 0
	task_num = int(task_num)
	results = {}	

	# instatiate jobHand object
	jobHand = jobs.jobStart()

	# set estimated number of tasks
	jobHand.estimated_tasks = task_num	
	while count < task_num:		
		result = actions.quickAdd.delay(41, 1, count)		
		jobHand.assigned_tasks.append(str(result))
		print count, result		
		results[count] = str(result)
		count += 1				

	# copy all tasks to pending
	jobHand.pending_tasks = jobHand.assigned_tasks[:]

	print "Finished job #",jobHand.job_num		

	# update job
	jobs.jobUpdate(jobHand)

	# TESTING OF CLASS METHODS
	# jobHand.update()

	return "You have initiated job {job_num}.  Click <a href='/job_status/{job_num}'>here</a> to check it foo.".format(job_num=jobHand.job_num)


@app.route("/longAdd/<task_num>")
def longAdd(task_num):
	print "Starting request..."
	# celery task deploying
	count = 0
	task_num = int(task_num)
	results = {}

	# instatiate jobHand object
	jobHand = jobs.jobStart()	

	# set estimated number of tasks
	jobHand.estimated_tasks = task_num	
	while count < task_num:		
		result = actions.longAdd.delay(41, 1, count)		
		jobHand.assigned_tasks.append(str(result))
		print count, result		
		results[count] = str(result)
		count += 1				

	# copy all tasks to pending
	jobHand.pending_tasks = jobHand.assigned_tasks[:]

	print "Finished job #",jobHand.job_num	

	# update job
	jobs.jobUpdate(jobHand)

	return "You have initiated job {job_num}.  Click <a href='/job_status/{job_num}'>here</a> to check it foo.".format(job_num=jobHand.job_num)


@app.route("/task_status/<task_id>")
def task_status(task_id):
	
	# global way to surgically pick task out of celery memory		
	result = actions.celery.AsyncResult(task_id)	
	state, retval = result.state, result.result
	response_data = dict(id=task_id, status=state, result=retval)
	
	return json.dumps(response_data)


	return "You are looking for {task_id}".format(task_id=task_id)	



@app.route("/job_status/<job_num>")
def job_status(job_num):		
	
	# start timer
	stime = time.time()

	# get job
	jobHand = jobs.jobGet(job_num)

	# check if pending jobs done
	if len(jobHand.pending_tasks) == 0:
		return "Job Complete!"
	
	# check if job has started at all!
	job_start_result = celery.AsyncResult(jobHand.assigned_tasks[0])				
	state = job_start_result.state
	print "Checking if job started..."
	if state == "PENDING":
		return "Job Pending, waiting for others to complete.  Isn't that polite?"

	# else, check all pending jobs
	print "Pre routing length of pending list",len(jobHand.pending_tasks)	
	pending_worker = jobHand.pending_tasks[:] 
	for task in pending_worker:		
		result = celery.AsyncResult(task)				
		state = result.state
		print "Checking task:",task,"/ State:",state
		
		# route based on state
		if state == "SUCCESS":
			jobHand.pending_tasks.remove(task)
			jobHand.completed_tasks.append(task)		

	print "POST routing length of pending list",len(jobHand.pending_tasks)

	etime = time.time()
	ttime = (etime - stime) * 1000
	print "Pending / Completion check took",ttime,"ms"	

	# update job
	jobs.jobUpdate(jobHand)	

	# check status	
	return "{completed} / {total} Completed.".format(completed=len(jobHand.completed_tasks),total=len(jobHand.assigned_tasks))


# Session Testing
@app.route("/sessionSet/<name>")
def sessionSet(name):	
	session['name'] = name
	return "You have changed the session name to {name}.".format(name=name)

@app.route("/sessionCheck")
def sessionCheck():		
	name = session['name']
	return "You have retrieved the session name {name}.".format(name=name)


# PID selection sandboxing
@app.route("/PIDselection", methods=['POST', 'GET'])
def PIDselection():
    form = forms.PIDselection(request.form)
    if request.method == 'POST':
        username = form.username.data
        PID = form.PID.data
        print form.data.viewkeys()
        # send PIDs to Redis
        jobs.sendSelectedPIDs(username,PID)
        return "We've got form data, your username is {username}, and your PID is {PID}.".format(username=username,PID=PID)                
    return render_template('PIDform.html', form=form)

@app.route("/PIDcheck/<username>")
def PIDcheck(username):	


	selectedPIDs = r_selectedPIDs_handle.lrange("{username}_selectedPIDs".format(username=username),0,-1)
	return "You have selected the following PID: {selectedPIDs}".format(selectedPIDs=selectedPIDs)


# Catch all - DON'T REMOVE
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













