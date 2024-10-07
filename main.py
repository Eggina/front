import os
from flask import Flask, Response, render_template, request, session, _app_ctx_stack, json
from services.database import SessionLocal
from services import figures
from services import calculador
import pandas as pd
from sqlalchemy.orm import scoped_session

app = Flask(__name__)

app.config['SECRET_KEY'] = ''
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

app.session = scoped_session(
    SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

indicadores = ['ipax', 'ikm', 'ipk', 'rpk',
               'itm', 'irt', 'ianac', 'ialoc', 'itp']

filename = os.path.join(app.static_folder, 'data', 'test_data.json')

with open(filename) as test_file:
    data = json.load(test_file)

indicadores_dict = dict()
for d in data['indicadores']:
    indicadores_dict[d['id']] = dict()
    indicadores_dict[d['id']] = d
indicadores_dict = calculador.setup_indicadores(indicadores_dict)
indicadores_dict = figures.setup_indicadores(indicadores_dict)


@app.route('/', methods=['GET', 'POST'])
def home():
    calc = calculador.Calculador()

    if not 'indicadores' in session:
        session['indicadores'] = dict()
        for ind in indicadores:
            session['indicadores'][ind] = 'absoluto'

    if request.method == 'POST':
        session['id_lineas'] = [id for id in request.form.getlist('lineas')]
        session['config'] = request.form.getlist('config')
        session['fecha'] = dict()
        session['fecha']['inicio'] = request.form.getlist('inicio')
        session['fecha']['fin'] = request.form.getlist('fin')
        session['indicadores'] = dict()
        for ind in indicadores:
            session['indicadores'][ind] = request.form.getlist(ind)

    lineas = calc.obtener_lineas(app.session)
    fechas = [pd.to_datetime(x).strftime(
        '%Y-%m') for x in calc.obtener_limites_fechas_validas(app.session)]
    app.session.remove()
    app.logger.info('Cargando home...')
    return render_template('home.html', indicadores=indicadores, lineas=lineas, fechas_extremas=fechas, session=session, asd=indicadores_dict)


@ app.route('/plot/<ind>')
def plot_png(ind=None):
    app.logger.info('Graficando {}...'.format(ind))
    output = figures.create_figure(ind, app.session, session, indicadores_dict)
    app.session.remove()
    return Response(output.getvalue(), mimetype='image/png')


@app.teardown_appcontext
def shutdown_session(exception=None):
    app.session.remove()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
