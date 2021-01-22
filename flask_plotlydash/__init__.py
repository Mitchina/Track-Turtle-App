# being called in wsgi.py
"""Initialize Flask app."""
from flask import Flask

def init_app(): # or create_app()
	"""Construct core Flask application."""
	app = Flask(__name__)#, instance_relative_config=False)
	# Connecting to a database utilizing a Redis store
	#app.config.from_object('config.Config')

	with app.app_context():
		# Import parts of our core Flask app
		# see if it is importing the file routes.py ****
		from . import routes

		"""Flask app with embedded Dash app."""
		# Import Dash application
		# from folder plotlydash and file dashboard
		# import the function init_dashboard or create_dashboard
		
		from .plotlydash.dashboard import init_dashboard
		# Register our isolated Dash app onto our parent Flask app: 
		app = init_dashboard(app)

		"""We're importing a file called dashboard.py from a 
		directory in our Flask app called /plotlydash. 
		Inside dashboard.py is a single function which 
		contains the entirety of a Plotly Dash app in itself"""

		return app



# Redis = a cloud key/value store
# If we decide at a later time that data in memory is worth keeping, 
# we can always write to disk (such as a SQL database) later on.

