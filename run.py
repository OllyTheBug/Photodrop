import os
# Get computer user's name
username = os.getlogin()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'C:\\Users\\{username}\\Documents\\instaclone.json'

# Local imports
from instaclone.__init__ import app
from instaclone.views import views




if __name__ == '__main__':
    
    # -------------------------------- Load views -------------------------------- #
    app.register_blueprint(views)
    app.run(host='localhost', port=8080, debug=True, use_reloader=False)
