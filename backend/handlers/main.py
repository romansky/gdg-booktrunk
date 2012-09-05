import httplib2,logging,os,webapp2,jinja2,json
from StringIO import StringIO
from pyPdf import PdfFileReader

from protomodels import BookListMessage,ReadEventMessage,UserInfoMessage,BookMessage
from model import User,Doc,ReadEvent

from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets,CredentialsProperty	
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache,users
from google.appengine.ext import db
from google.appengine.ext.db import Key

from protorpc import remote,message_types
from protorpc.wsgi import service as protoservice

jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

http = httplib2.Http(memcache)
service = build("drive", "v2", http=http)
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=['https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/userinfo.email'],
    message=MISSING_CLIENT_SECRETS_MESSAGE)


class MainPage(webapp2.RequestHandler):
	@decorator.oauth_required
	def get(self):
		http = decorator.http()
		# Call the service using the authorized Http object.
		request = service.files().list()
		response = request.execute(http=http)
		resultlist = []
		for f in filter(lambda x:x['mimeType'] == 'application/pdf' and not x['labels']['trashed'],response['items']):
			downloadUrl = f.get('downloadUrl')
			if downloadUrl:
				logging.info('Request file %s' % f['title'])	
				resp, content = http.request(downloadUrl)
				if resp.status == 200:
					logging.info('Request successful')
					pdfobj = PdfFileReader(StringIO(content))
					f['numpages'] = pdfobj.getNumPages()
					resultlist.append(f)				
				else:
					logging.error('An error occured %s' % resp)
			else:
				logging.info('No download url for file %s' % f['title'])

		logging.info('User email: %s' % users.get_current_user().email())
		curUser = User.get_or_insert(users.get_current_user().email(),email=users.get_current_user().email())
		for f in resultlist:
			Doc.get_or_insert(f['id'],parent=curUser.key(),title=f['id'],totalPages=f['numpages'],user=curUser)

		template_values = {
			'filelist' : resultlist
		}
		template = jinja_environment.get_template('home.html')
		self.response.out.write(template.render(template_values))

class ApiService(remote.Service):
	@remote.method(UserInfoMessage,BookListMessage)
	def list(self,request):
		q=User.get(Key.from_path('User',request.user_email))
		results = q.documents
		logging.info(results)
		messagesdocs = map(lambda doc:BookMessage(bookid=doc.key().name(),total_pages=doc.totalPages,current_page=doc.currentPage),results)
		return BookListMessage(books=messagesdocs)

	@remote.method(ReadEventMessage,message_types.VoidMessage)
	def readevent(self,request):
		pass

app = webapp2.WSGIApplication([ ('/',MainPage),(decorator.callback_path, decorator.callback_handler())],debug=True)
api = protoservice.service_mapping(ApiService)