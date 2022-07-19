from instaclone.__init__ import app

def check_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_TYPES']
