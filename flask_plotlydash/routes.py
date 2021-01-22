# being called in __init__.py
# Creating a Flask Homepage
"""We now have the freedom to build an app without restriction, 
jumping in or out of Plotly Dash on the views we see fit. """

"""Flask expects the templates directory to be in the same 
folder as the module in which it was created. You can specify 
he location of the template_folder.
app = Flask(__name__, template_folder='../pages/templates') """


"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app # defining app in @app.route


@app.route('/')
def index(): # or home
	"""Landing page."""
	title = "homepage"
	return render_template('base.html', #change to index to play with changes
		title= title) # 'Plotly Dash Flask Tutorial',
		#description='Embed Plotly Dash into your Flask applications.',
		#template='index-template',
		#body="This is a homepage served with Flask.")


#@app.route('/user/<username>')
#def user(username):
	#return render_template('user.html', username=username)

#@app.errorhandler(404)
#def page_not_found(e):
	# see method GET and POST
	# if request.method == 'POST':
		# return redirect(url_for('index'))
    #return render_template('404.html'), 404