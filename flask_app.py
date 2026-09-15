import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-aula-050'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- MODELOS DE BANCO DE DADOS ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# --- FORMULÁRIOS ---
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', coerce=int)
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators=[DataRequired()])
    senha = PasswordField('Informe a sua senha', validators=[DataRequired()])
    submit = SubmitField('Enviar')


# --- ROTAS PRINCIPAIS ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    current_time = datetime.utcnow()
    
    # Preenche o formulário com a sintaxe correta para evitar o Erro 500
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]

    if form.validate_on_submit():
        # Lógica de alerta (flash)
        old_name = session.get('name')
        if old_name is None or old_name != form.name.data:
            flash('Você alterou o seu nome!')

        # Lógica do Banco de Dados
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            selected_role = Role.query.get(form.role.data)
            user = User(username=form.name.data, role=selected_role)
            db.session.add(user)
            db.session.commit()
            
        session['name'] = form.name.data
        return redirect(url_for('index'))

    # Consultas para as tabelas do HTML
    users = User.query.all()
    roles = Role.query.all()

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        users=users,
        roles=roles,
        remote_addr=request.remote_addr,
        host=request.host,
        current_time=current_time,
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    current_time = datetime.utcnow()
    usuario_logado = None

    if form.validate_on_submit():
        usuario_logado = form.usuario.data

    return render_template(
        'login.html',
        form=form,
        usuario=usuario_logado,
        current_time=current_time,
    )


if __name__ == '__main__':
    app.run(debug=True)