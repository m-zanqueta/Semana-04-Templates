from flask import Flask, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-aula-flask'

bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # Salva o nome digitado na sessão do navegador
        session['name'] = form.name.data
        return redirect(url_for('index'))

    # Busca o nome salvo na sessão (retorna None se não houver)
    name = session.get('name')
    return render_template('index.html', form=form, name=name)


if __name__ == '__main__':
    app.run(debug=True)