import os
from dotenv import load_dotenv
import requests
from flask import Flask, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-flasky'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Credenciais do SendGrid configuradas no seu .env
app.config['API_KEY'] = os.environ.get('API_KEY', '')
app.config['API_URL'] = os.environ.get('API_URL', 'https://api.sendgrid.com/v3/mail/send')
app.config['API_FROM'] = os.environ.get('API_FROM', 'm.zanqueta@aluno.ifsp.edu.br')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Avaliação Contínua]'

STUDENT_PRONTUARIO = "PT3035875"
STUDENT_NAME = "Matheus Zanqueta"

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    send_email_prof = BooleanField('Deseja enviar e-mail para flaskaulasweb@zohomail.com?')
    submit = SubmitField('Submit')


def send_email(to_list, subject, template, **kwargs):
    if not app.config['API_URL'] or not app.config['API_KEY']:
        print("Erro: API_KEY não encontrada no .env")
        return None

    try:
        html_content = render_template(template + '.html', **kwargs)
        headers = {
            "Authorization": f"Bearer {app.config['API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "personalizations": [{"to": [{"email": email} for email in to_list]}],
            "from": {"email": app.config['API_FROM']},
            "subject": f"{app.config['FLASKY_MAIL_SUBJECT_PREFIX']} {subject}",
            "content": [{"type": "text/html", "value": html_content}]
        }
        response = requests.post(app.config['API_URL'], json=payload, headers=headers)
        return response.status_code
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            
            # Lógica da Caixinha (Checkbox):
            destinatarios = ['m.zanqueta@aluno.ifsp.edu.br']
            if form.send_email_prof.data: # Se a caixinha estiver marcada
                destinatarios.append('flaskaulasweb@zohomail.com')
            
            send_email(
                to_list=destinatarios,
                subject='Novo Usuário Cadastrado',
                template='mail/new_user',
                username=form.name.data,
                student_name=STUDENT_NAME,
                prontuario=STUDENT_PRONTUARIO
            )
        else:
            session['known'] = True
            
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
            
        session['name'] = form.name.data
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('index.html', form=form, name=session.get('name'), 
                           known=session.get('known', False), users=users)


if __name__ == '__main__':
    app.run(debug=True)