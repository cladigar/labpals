import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'labpals.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USER_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['armandgonzalez1994@gmail.com']
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'tex', 'csv', 'ppt', 'pps', 'pptx', 'jpg', 'png', 'tif', 'xls',
                          'xlsx', 'pdb', 'fa', 'fasta', 'gif', 'epub'}
    UPLOAD_FOLDER = os.path.join(basedir, 'labpals/uploads')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ENTRIES_PER_PAGE = 10
