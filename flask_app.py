import os
from datetime import datetime
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

# Configurações do SendGrid
app.config['API_KEY'] = os.environ.get('API_KEY', '')
app.config['API_URL'] = os.environ.get('API_URL', 'https://api.sendgrid.com/v3/mail/send')
app.config['API_FROM'] = os.environ.get('API_FROM', 'm.zanqueta@aluno.ifsp.edu.br')
# Ajuste do prefixo para corresponder à imagem
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' 

STUDENT_PRONTUARIO = "PT3035875"
STUDENT_NAME = "Matheus Zanqueta"

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ==========================================
# MODELOS DE BASE DE DADOS
# ==========================================
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

class SentEmail(db.Model):
    __tablename__ = 'sent_emails'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(64))
    recipients = db.Column(db.String(256))
    subject = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)


# ==========================================
# FORMULÁRIOS E E-MAIL
# ==========================================
class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    send_email_prof = BooleanField('Deseja enviar e-mail para flaskaulasweb@zohomail.com?')
    submit = SubmitField('Submit')

def send_email(to_list, subject, template, **kwargs):
    if not app.config['API_URL'] or not app.config['API_KEY']:
        print("Erro: API_KEY não encontrada")
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


# ==========================================
# ROTAS
# ==========================================
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
            
            # Lógica dos destinatários
            destinatarios = ['m.zanqueta@aluno.ifsp.edu.br']
            if form.send_email_prof.data:
                destinatarios.append('flaskaulasweb@zohomail.com')
                # Formatação em string para reproduzir a coluna "Para" da imagem
                recipients_str = "['m.zanqueta@aluno.ifsp.edu.br', 'flaskaulasweb@zohomail.com']"
            else:
                recipients_str = "'m.zanqueta@aluno.ifsp.edu.br'"
            
            # Persistir o e-mail na base de dados
            novo_email = SentEmail(
                sender_name=form.name.data,
                recipients=recipients_str,
                subject="[Flasky] Novo usuário",
                body=f"Novo usuário cadastrado: {form.name.data}"
            )
            db.session.add(novo_email)
            db.session.commit()
            
            # Disparar o e-mail
            send_email(
                to_list=destinatarios,
                subject='Novo usuário',
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


@app.route('/emails')
def emails():
    # Carrega os e-mails ordenados pelos mais recentes
    sent_emails = SentEmail.query.order_by(SentEmail.timestamp.desc()).all()
    return render_template('emails.html', emails=sent_emails)


if __name__ == '__main__':
    app.run(debug=True)