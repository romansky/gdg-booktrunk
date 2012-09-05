from protorpc import messages

class UserInfoMessage(messages.Message):
	user_email		= messages.StringField(1,required=True)

class BookMessage(messages.Message):
	bookid			= messages.StringField(1,required=True)
	total_pages		= messages.IntegerField(2)
	current_page	= messages.IntegerField(3)

class BookListMessage(messages.Message):
	books 			= messages.MessageField(BookMessage,1,repeated=True)

class ReadEventMessage(messages.Message):
	user_email		= messages.StringField(1,required=True)
	bookid			= messages.StringField(2,required=True)
	start_page		= messages.IntegerField(3,required=True)
	end_page		= messages.IntegerField(4,required=True)
	start_dt		= messages.StringField(5,required=True)
	end_dt			= messages.StringField(6,required=True)