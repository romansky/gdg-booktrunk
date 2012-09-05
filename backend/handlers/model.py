from google.appengine.ext import db

class User(db.Model):
	user 		= db.UserProperty(auto_current_user_add=True)
	email		= db.StringProperty()

class Doc(db.Model):
	title 		= db.StringProperty(required=True)
	totalPages 	= db.IntegerProperty(default=0)
	currentPage = db.IntegerProperty(default=0)
	user		= db.ReferenceProperty(User,collection_name='documents')

class ReadEvent(db.Model):
	doc			= db.ReferenceProperty(Doc,collection_name='events')
	startPage	= db.IntegerProperty()
	endPage		= db.IntegerProperty()
	startTime	= db.DateTimeProperty()
	endTime		= db.DateTimeProperty()