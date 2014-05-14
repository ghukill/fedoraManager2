from wtforms import Form, BooleanField, StringField, validators, fields

class PIDselection(Form):    
    PID = fields.FieldList(fields.TextField(('PID')), min_entries=3)
    