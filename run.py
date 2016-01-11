from application import app
from application import CONFIG

if __name__ =="__main__":
	app.run(debug = CONFIG["DEBUG"])