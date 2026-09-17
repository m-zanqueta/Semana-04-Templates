import os
from dotenv import load_dotenv
import requests
from flask import Flask, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-flasky'

app.config['API_KEY'] = os.environ.get('API_KEY', '')
app.config['API_URL'] = os.environ.get('API_URL', 'https://api.sendgrid.com/v3/mail/send')
app.config['API_FROM'] = os.environ.get('API_FROM', 'm.zanqueta@aluno.ifsp.edu.br')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'

STUDENT_PRONTUARIO = "PT3035875"
STUDENT_NAME = "Matheus Zanqueta"
RECIPIENTS = ['flaskaulasweb@zohomail.com','m.zanqueta@aluno.ifsp.edu.br']

bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


def send_email(to_list, subject, template, **kwargs):
    if not app.config['API_URL'] or not app.config['API_KEY']:
        print("Erro: API_KEY ou API_URL ausentes no .env")
        return None

    try:
        html_content = render_template(template + '.html', **kwargs)
        headers = {
            "Authorization": f"Bearer {app.config['API_KEY']}",
            "Content-Type": "application/json"
        }

        # Estrutura do payload exigido pela API v3 do SendGrid
        payload = {
            "personalizations": [
                {
                    "to": [{"email": email} for email in to_list]
                }
            ],
            "from": {"email": app.config['API_FROM']},
            "subject": f"{app.config['FLASKY_MAIL_SUBJECT_PREFIX']} {subject}",
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }

        response = requests.post(app.config['API_URL'], json=payload, headers=headers)
        print(f"SendGrid Status Code: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"Erro ao enviar e-mail via SendGrid: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is None or old_name != form.name.data:
            flash('Looks like you have changed your name!')

            send_email(
                to_list=RECIPIENTS,
                subject='Novo Usuário Cadastrado',
                template='mail/new_user',
                username=form.name.data,
                student_name=STUDENT_NAME,
                prontuario=STUDENT_PRONTUARIO
            )

        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'))


if __name__ == '__main__':
    app.run(debug=True)