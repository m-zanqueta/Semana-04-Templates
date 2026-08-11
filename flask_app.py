from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route('/')
def index():
    current_time = datetime.utcnow()
    return render_template('index.html', current_time=current_time)


@app.route('/identificacao')
def identificacao():
    nome = "Matheus Zanqueta Vitor"
    prontuario = "PT3035875"
    instituicao = "IFSP"
    return render_template(
        'identificacao.html',
        nome=nome,
        prontuario=prontuario,
        instituicao=instituicao,
    )


@app.route('/contexto')
def contexto():
    nome = "Matheus Zanqueta Vitor"
    user_agent = request.headers.get('User-Agent')
    remote_addr = request.remote_addr
    host = request.host
    return render_template(
        'contexto.html',
        nome=nome,
        user_agent=user_agent,
        remote_addr=remote_addr,
        host=host,
    )


if __name__ == '__main__':
    app.run(debug=True)