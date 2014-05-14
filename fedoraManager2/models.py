from fedoraManager2 import db


class jobBlob:
	def __init__(self, job_num):
		self.job_num = job_num
		self.estimated_tasks = ''
		self.assigned_tasks = []
		self.pending_tasks = []
		self.completed_tasks = []
		self.error_tasks = []

class taskBlob:
	def __init__(self, job_num):
		self.job_num = job_num		
		self.estimated_tasks = ''
		self.last_completed_task_num = 'pending'
		self.completed_tasks = []



class selectedPID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PID = db.Column(db.String(120), unique=True)    

    def __init__(self, PID):
        self.PID = PID        

    def __repr__(self):
        return '<PID %r>' % self.PID