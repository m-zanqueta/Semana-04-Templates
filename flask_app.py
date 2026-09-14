import os
from flask import Flask, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Define o diretório base para salvar o arquivo do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta'

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# Desativa o rastreamento de modificações para economizar memória
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

bootstrap = Bootstrap(app)

# Inicializa o SQLAlchemy[cite: 1]
db = SQLAlchemy(app)
# Inicializa o Flask-Migrate[cite: 1]
migrate = Migrate(app, db)


# --- DEFINIÇÃO DOS MODELOS ---
# Classe Role (Funções)[cite: 1]
class Role(db.Model):
    __tablename__ = 'roles' # Define o nome da tabela[cite: 1]
    id = db.Column(db.Integer, primary_key=True) # Chave primária[cite: 1]
    name = db.Column(db.String(64), unique=True)
    # Relacionamento um-para-muitos com a classe User[cite: 1]
    users = db.relationship('User', backref='role', lazy='dynamic') 

    def __repr__(self):
        return '<Role %r>' % self.name


# Classe User (Usuários)[cite: 1]
class User(db.Model):
    __tablename__ = 'users' # Define o nome da tabela[cite: 1]
    id = db.Column(db.Integer, primary_key=True) # Chave primária[cite: 1]
    username = db.Column(db.String(64), unique=True, index=True)
    # Chave estrangeira ligando à tabela roles[cite: 1]
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) 

    def __repr__(self):
        return '<User %r>' % self.username


# --- FORMULÁRIO ---
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    # Campo de seleção para as funções
    role = SelectField('Role?:', coerce=int)
    submit = SubmitField('Submit')


# --- ROTAS ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    
    # Preenche o formulário com as opções de funções do banco de dados[cite: 1]
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by('name').all()]

    if form.validate_on_submit():
        # Verifica se o usuário já existe no banco consultando o banco[cite: 1]
        user = User.query.filter_by(username=form.name.data).first()
        
        if user is None:
            # Pega o objeto da função (Role) com base na escolha do usuário[cite: 1]
            selected_role = Role.query.get(form.role.data)
            
            # Cria a instância do novo usuário atrelando à função[cite: 1]
            user = User(username=form.name.data, role=selected_role)
            
            # Adiciona e grava o objeto no banco de dados[cite: 1]
            db.session.add(user)
            db.session.commit()
            
        session['name'] = form.name.data
        return redirect(url_for('index'))

    # Consulta todos os usuários e todas as funções para exibir nas tabelas[cite: 1]
    users = User.query.all()
    roles = Role.query.all()

    return render_template(
        'index.html', 
        form=form, 
        name=session.get('name'), 
        users=users, 
        roles=roles
    )


if __name__ == '__main__':
    app.run(debug=True)