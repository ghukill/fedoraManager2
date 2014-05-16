from fedoraManager2 import app
from fedoraManager2 import models
from fedoraManager2 import db
from fedoraManager2.actions import actions


# flask proper
from flask import render_template, request, session, redirect, make_response
from flask.ext.sqlalchemy import SQLAlchemy

# forms
from flask_wtf import Form
from wtforms import TextField

# zato paginator
from zato.redis_paginator import ListPaginator, ZSetPaginator

import time
import json
import pickle
import sys
import importlib
import pprint

# get celery instance / handle
from cl.cl import celery
import jobs
import forms
from redisHandles import *

from uuid import uuid4

# fake session data
####################################
# set the secret key
app.secret_key = 'ShoppingHorse'
####################################

@app.route("/")
def index():
	return render_template("index.html")
	


# @app.route("/task_status/<task_id>")
# def task_status(task_id):
	
# 	# global way to surgically pick task out of celery memory		
# 	result = actions.celery.AsyncResult(task_id)	
# 	state, retval = result.state, result.result
# 	response_data = dict(id=task_id, status=state, result=retval)
	
# 	return json.dumps(response_data)


# 	return "You are looking for {task_id}".format(task_id=task_id)		



# Session Testing
@app.route("/sessionSet/<username>")
def sessionSet(name):	
	session['username'] = username
	return "You have changed the session username to {username}.".format(username=username)

@app.route("/sessionCheck")
def sessionCheck():		
	username = session['username']
	return "You have retrieved the session username {username}.".format(username=username)

@app.route('/userPage/<username>')
def userPage(username):
	# set username in session
	session['username'] = username	

	# info to render page
	userData = {}
	userData['username'] = username
	return render_template("userPage.html",userData=userData)

# JOB MANAGEMENT
#########################################################################################################


# fireTask is the factory that begins tasks from fedoraManager2.actions
# epecting task function name from actions module, e.g. "sampleTask"
@app.route("/fireTask/<task_name>")
def fireTask(task_name):
	print "Starting taskv3 request..."
	
	# get username from session (will pull from user auth session later)
	username = session['username']	
	# get total PIDs associated with user
	userPID_pag = models.user_pids.query.paginate(1,5)

	# instatiate jobHand object with incrementing job_num
	jobInit = jobs.jobStart()
	jobHand = jobInit['jobHand']
	taskHand = jobInit['taskHand']

	job_num = jobHand.job_num

	# begin job
	print "Antipcating",userPID_pag.total,"tasks...."
	# push estimated tasks to jobHand and taskHand
	jobHand.estimated_tasks = userPID_pag.total
	taskHand.estimated_tasks = userPID_pag.total
	
	# create job_package
	job_package = {		
		"username":username,
		"job_num":job_num,
		"jobHand":jobHand		
	}

	# grab task from actions based on URL "task_name" parameter, using getattr	
	task_function = getattr(actions, task_name)

	# send to celeryTaskFactory in actions.py
	# iterates through PIDs and creates secondary async tasks for each
	# passing username, task_name, task_function as imported above, and job_package containing all the update handles		
	result = actions.celeryTaskFactory.delay(job_num=job_num,task_name=task_name,task_function=task_function,job_package=job_package)

	# preliminary update
	jobs.jobUpdate(jobHand)		
	jobs.taskUpdate(taskHand)

	print "Started job #",jobHand.job_num

	return redirect("/jobStatus/{job_num}?jobInit=true".format(job_num=jobHand.job_num))

#SLATED FOR REMOVAL TO SQL
##################################################################################################################################
# # fireTask is the factory that begins tasks from fedoraManager2.actions
# # epecting task function name from actions module, e.g. "sampleTask"
# @app.route("/fireTask/<task_name>")
# def fireTask(task_name):
# 	print "Starting taskv3 request..."
	
# 	# get username from session (will pull from user auth session later)
# 	username = session['username']	
# 	# get total PIDs associated with user
# 	userPag = jobs.userPagGen(username)	

# 	# instatiate jobHand object with incrementing job_num
# 	jobInit = jobs.jobStart()
# 	jobHand = jobInit['jobHand']
# 	taskHand = jobInit['taskHand']

# 	job_num = jobHand.job_num

# 	# begin job
# 	print "Antipcating",userPag.count,"tasks...."
# 	# push estimated tasks to jobHand and taskHand
# 	jobHand.estimated_tasks = userPag.count
# 	taskHand.estimated_tasks = userPag.count
	
# 	# create job_package
# 	job_package = {		
# 		"username":username,
# 		"job_num":job_num,
# 		"jobHand":jobHand		
# 	}

# 	# grab task from actions based on URL "task_name" parameter, using getattr	
# 	task_function = getattr(actions, task_name)

# 	# send to celeryTaskFactory in actions.py
# 	# iterates through PIDs and creates secondary async tasks for each
# 	# passing username, task_name, task_function as imported above, and job_package containing all the update handles		
# 	result = actions.celeryTaskFactory.delay(job_num=job_num,task_name=task_name,task_function=task_function,job_package=job_package)

# 	# preliminary update
# 	jobs.jobUpdate(jobHand)		
# 	jobs.taskUpdate(taskHand)

# 	print "Started job #",jobHand.job_num

# 	return redirect("/jobStatus/{job_num}?jobInit=true".format(job_num=jobHand.job_num))
##################################################################################################################################

@app.route("/jobStatus/<job_num>")
def jobStatus(job_num):		
	
	# start timer
	stime = time.time()

	# create package
	status_package = {}
	status_package["job_num"] = job_num

	# get job
	jobHand = jobs.jobGet(job_num)
	taskHand = jobs.taskGet(job_num)
	taskHand.last_completed_task_num = len(taskHand.completed_tasks)

	# DEBUG
	# print "length of jobHand assigned:", len(jobHand.assigned_tasks)
	# print "integer of jobHand estimated tasks:",int(jobHand.estimated_tasks)
	# print "taskHand.completed_tasks:",taskHand.completed_tasks
	# print "length of taskHand.completed_tasks:",len(taskHand.completed_tasks)	

	# spooling, works on stable jobHand object
	if len(jobHand.assigned_tasks) > 0 and len(jobHand.assigned_tasks) < int(jobHand.estimated_tasks) :
		print "Job spooling..."
		status_package['job_status'] = "spooling"

	# check if pending jobs done
	elif len(taskHand.completed_tasks) == 0:
		print "Job Pending, waiting for others to complete.  Isn't that polite?"
		status_package['job_status'] = "pending"		

	elif len(taskHand.completed_tasks) == taskHand.estimated_tasks:			
		print "Job Complete!"
		status_package['job_status'] = "complete"		

	else:
		status_package['job_status'] = "running"
		etime = time.time()
		ttime = (etime - stime) * 1000
		print "Pending / Completion check took",ttime,"ms"

	# data return 
	if request.args.get("data","") == "true":
		response_dict = {
			"job_status":status_package['job_status'],
			"completed_tasks":len(taskHand.completed_tasks),
			"estimated_tasks":taskHand.estimated_tasks
		}
		json_string = json.dumps(response_dict)
		print json_string
		resp = make_response(json_string)
		resp.headers['Content-Type'] = 'application/json'
		return resp

	# render human page (this will probably go the way of the dodo with jobs dashboard)
	if request.args.get("jobInit","") == "true":
		status_package['jobInit'] = "true"
	return render_template("jobStatus.html",username=session['username'],status_package=status_package,jobHand=jobHand,taskHand=taskHand)


# PID MANAGEMENT
####################################################################################

@app.route("/PIDselectionSQL", methods=['POST', 'GET'])
def PIDselectionSQL():	

	# get username from session
	username = session['username']
	form = forms.PIDselection(request.form)

	if request.method == 'POST':		 
		PID = form.PID.data				
		jobs.sendUserPIDs(username,PID)
		return redirect("/PIDmanage/1")		

	return render_template('PIDformSQL.html', username=username, form=form)# PID selection sandboxing

# PID check for user
@app.route("/PIDmanage/<pagenum>")
def PIDmanage(pagenum):	
	# get username from session
	username = session['username']

	# pass the current PIDs to page as list	
	return render_template("PIDSQL.html",username=username,pagenum=int(pagenum))



# SLATED FOR REMOVAL, MOVING TO SQLalchemy
################################################################################################################################################
# # PID selection sandboxing
# @app.route("/PIDselectionUser", methods=['POST', 'GET'])
# def PIDselectionUser():
# 	# get username from session
# 	username = session['username']
# 	form = forms.PIDselection(request.form)
# 	if request.method == 'POST':		
# 		PID = form.PID.data				
# 		jobs.sendSelectedPIDs(username,PID)
# 		return redirect("/PIDmanage/1".format(username=username))
# 		return "We've got form data, your username is {username}, and your PIDs are {PID}.".format(username=username,PID=PID)                
# 	return render_template('PIDformUser.html', username=username, form=form)# PID selection sandboxing

# PID check for user
# @app.route("/PIDmanage/<pagenum>")
# def PIDmanage(pagenum):
# 	# start timer
# 	stime = time.time()

# 	# get username from session
# 	username = session['username']	

# 	# entirety of pagination code - lightning fast, can break this out somewhere else	
# 	userPag = jobs.userPagGen(username)	
# 	print "Found {count} PIDs for {username}".format(count=userPag.count,username=username)
# 	print "Paginator is",sys.getsizeof(userPag),"bytes"
# 	print "You have {PID_count} PIDs, will need {page_count} pages.".format(PID_count=userPag.count,page_count=userPag.num_pages)				
# 	cpage = userPag.page(pagenum)	

# 	# report time passed	
# 	etime = time.time()
# 	ttime = (etime - stime) * 1000
# 	print "PID retrieval took",ttime,"ms"	

# 	# pass the current PIDs to page as list	
# 	return render_template("PIDmanage.html",cpage_PIDs=cpage.object_list,username=username,userPag=userPag,cpage=cpage,pagenum=int(pagenum))
################################################################################################################################################




# Catch all - DON'T REMOVE
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













