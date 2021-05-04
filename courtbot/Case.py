class Case():
    """Some sort of generalized object that will be constructed identically for every state"""
    def __init__(self, *, case_id, when, what, cellphone, origination=None):
        self.case_id = case_id
        self.when = when
        self.what = what
        self.cellphone = cellphone
        self.origination = origination


    def save(db):
        db.execute('INSERT INTO reminders (...) VALUES (...)', ...)
        return db.commit() # some sort of "true" / "false" value to confirm persistence?
