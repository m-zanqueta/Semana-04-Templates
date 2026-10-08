import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-secreta-flasky')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do SendGrid
    API_KEY = os.environ.get('API_KEY', '')
    API_URL = os.environ.get('API_URL', 'https://api.sendgrid.com/v3/mail/send')
    API_FROM = os.environ.get('API_FROM', 'm.zanqueta@aluno.ifsp.edu.br')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'

    # Dados do Aluno
    STUDENT_PRONTUARIO = "PT3035875"
    STUDENT_NAME = "Matheus Zanqueta"

    @staticmethod
    def init_app(app):
        pass