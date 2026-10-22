import os
import requests
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import NameForm
from .. import db
from ..models import User

api_key = os.environ.get('SENDGRID_API_KEY')

def enviar_notificacao_sendgrid(novo_usuario, email_usuario):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "personalizations": [{
            "to": [
                {"email": "flaskaulasweb@zohomail.com"},
                {"email": "m.zanqueta@aluno.ifsp.edu.br"},
                {"email": email_usuario}
            ]
        }],
        "from": {"email": "m.zanqueta@aluno.ifsp.edu.br"},
        "subject": "Semana 12 - Novo Usuário Cadastrado",
        "content": [{
            "type": "text/html",
            "value": f"""
            <h3>Novo Cadastro na Aplicação</h3>
            <p><strong>Prontuário do aluno:</strong> PT3035875</p>
            <p><strong>Nome do aluno:</strong> Matheus Zanqueta</p>
            <hr>
            <p><strong>Novo usuário cadastrado:</strong> {novo_usuario}</p>
            <p><strong>E-mail de contato:</strong> {email_usuario}</p>
            """
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code not in [200, 201, 202]:
            flash(f"Erro do SendGrid ({response.status_code}): {response.text}")
    except Exception as e:
        flash(f"Falha de ligação à API: {str(e)}")

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()

            session['known'] = False
            enviar_notificacao_sendgrid(user.username, form.email.data)
        else:
            session['known'] = True

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))

    users = User.query.all()

    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           users=users)