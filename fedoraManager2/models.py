
# dp
import pickle
import redis

class jobBlob:	

	def __init__(self, job_num):
		self.job_num = job_num
		self.estimated_tasks = ''
		self.assigned_tasks = []
		self.pending_tasks = []
		self.completed_tasks = []
		self.error_tasks = []

	# NEEDS MUCH MORE INVESTIGATING
	############################################################################
	# 	# redis handle
	# 	self.r_batch_handle = redis.StrictRedis(host='localhost', port=6379, db=2)

	# def update(self):		
	# 	print type(self)
	# 	print dir(self)
	# 	jobHand_pickled = cloud.serialization.cloudpickle.dumps(self)
	# 	self.r_batch_handle.set("job_{job_num}".format(job_num=self.job_num),jobHand_pickled)
	############################################################################