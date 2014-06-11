from wtforms import Form, BooleanField, StringField, validators, fields

################################################################################################################
# this is essentially temporary - selection will come from the results of Solr, Fed, Risearch
################################################################################################################

class PIDselection(Form):    
    PID = fields.FieldList(fields.TextField(('PID')), min_entries=3)
    

class solrSearch(Form):
	q = StringField('query (q)')
	fq = StringField('filter query (fq_')
	fl = StringField('fields to return (fl)')
