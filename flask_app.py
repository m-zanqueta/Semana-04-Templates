from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-aula-050'

bootstrap = Bootstrap(app)
moment = Moment(app)


class InfoForm(FlaskForm):
    nome = StringField('Informe o seu nome', validators=[DataRequired()])
    sobrenome = StringField(
        'Informe o seu sobrenome:', validators=[DataRequired()]
    )
    instituicao = StringField(
        'Informe a sua Insituição de ensino:', validators=[DataRequired()]
    )
    disciplina = SelectField(
        'Informe a sua disciplina:',
        choices=[
            ('DSWA5', 'DSWA5'),
            ('DWBA4', 'DWBA4'),
            ('Gestão de projetos', 'Gestão de projetos'),
        ],
    )
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators=[DataRequired()])
    senha = PasswordField('Informe a sua senha', validators=[DataRequired()])
    submit = SubmitField('Enviar')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    current_time = datetime.utcnow()

    if form.validate_on_submit():
        old_nome = session.get('nome')
        # Exibe o alerta se o nome informado for diferente do nome anterior guardado na sessão
        if old_nome is not None and old_nome != form.nome.data:
            flash('Você alterou o seu nome!')

        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        return redirect(url_for('index'))

    return render_template(
        'index.html',
        form=form,
        nome=session.get('nome'),
        sobrenome=session.get('sobrenome'),
        instituicao=session.get('instituicao'),
        disciplina=session.get('disciplina'),
        remote_addr=request.remote_addr,
        host=request.host,
        current_time=current_time,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    current_time = datetime.utcnow()

    if form.validate_on_submit():
        session['usuario'] = form.usuario.data
        return redirect(url_for('login'))

    return render_template(
        'login.html',
        form=form,
        usuario=session.get('usuario'),
        current_time=current_time,
    )


if __name__ == '__main__':
    app.run(debug=True)