# calling file __init__.py inside flask_plotlydash folder
# that contains the function create_app in it
from flask_plotlydash import init_app

app = init_app() # or create_app()


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=4000 ,debug=True)