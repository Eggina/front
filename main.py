import io
from flask import Flask, Response, render_template, request, session, _app_ctx_stack
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from matplotlib import pyplot as plt

from time import strptime, strftime
***REMOVED***
import seaborn as sns
from model.calculador import Calculador

import secrets
from database import db_session


***REMOVED***

app.config['SECRET_KEY'] = '1jAqXjc1hFqjas2ks5PoAw'
***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
    global db_session

    calculador = Calculador()

***REMOVED***
***REMOVED***
***REMOVED***
        session['inicio'] = request.form.getlist('inicio')
        session['fin'] = request.form.getlist('fin')

    lineas = calculador.obtener_lineas(db_session)
    fechas = [x[:7]
              for x in calculador.obtener_limites_fechas_validas(db_session)]

    return render_template('home.html', lineas=lineas, fechas_extremas=fechas, session=session)


***REMOVED***
***REMOVED***
    global db_session
    fig = create_figure(ind, db_session)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
***REMOVED***


***REMOVED***
***REMOVED***
    db_session.remove()


def create_figure(ind, db_session):

    fig = Figure(figsize=(8.09, 5), tight_layout=True)
    axis = fig.add_subplot(1, 1, 1)

    if session.get('id_lineas'):
        calculador = Calculador()

        table = pd.DataFrame()

        id_lineas = session.get('id_lineas')
        id_lineas = ['\"{}\"'.format(x) for x in id_lineas]

        config = dict()
        config['title'] = ''
        config['ylabel'] = ''
        config['formatter'] = None

        if ind == 'ipax':
            table = calculador.calcular_IPAX(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Evolución de pasajeros mensual'
            config['ylabel'] = '% cambio interanual'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
        if ind == 'ikm':
            table = calculador.calcular_IKM(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Evolución de kilómetros mensual'
            config['ylabel'] = '% cambio interanual'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
        if ind == 'ipk':
            table = calculador.calcular_IPK(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Pasajeros por kilómetro'
            config['ylabel'] = 'Pasajeros por km'
            config['formatter'] = mticker.ScalarFormatter()
        if ind == 'rpk':
            table = calculador.calcular_RPK(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Recaudación por kilómetro (sin compensaciones)'
            config['ylabel'] = '$ por km'
            config['formatter'] = mticker.ScalarFormatter()
        if ind == 'itm':
            table = calculador.calcular_ITM(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Tarifa media'
            config['ylabel'] = '$'
            config['formatter'] = mticker.ScalarFormatter()
        if ind == 'irt':
            table = calculador.calcular_IRT(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Rendimiento tarifario'
            config['ylabel'] = '% de tarifa plana'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
        if ind == 'at_nac':
            table = calculador.calcular_AT_Nac(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Pasajeros con tarifa preferencial nacional'
            config['ylabel'] = '% pasajeros'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
        if ind == 'at_loc':
            table = calculador.calcular_AT_Loc(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Pasajeros con tarifa preferencial local'
            config['ylabel'] = '% pasajeros'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
        if ind == 't_plana':
            table = calculador.calcular_T_Plana(
                session['inicio'][0], session['fin'][0], id_lineas, 'agregadas' in session.get('config'), db_session).reset_index()
            config['title'] = 'Pasajeros pagando tarifa plana'
            config['ylabel'] = '% pasajeros'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))

        if not table.empty:
            custom_palette = sns.color_palette(
                "Paired", len(session.get('id_lineas')))

            if not 'agregadas' in session.get('config') and not 'agrupadas' in session.get('config'):
                sns.lineplot(x=table.columns[0], y=table.columns[-1],
                             data=table, hue=table.columns[1], ax=axis, legend="full", palette=custom_palette, marker='o')
            else:
                sns.lineplot(
                    x=table.columns[0], y=table.columns[-1], data=table, ax=axis, legend="full", palette=custom_palette, marker='o')

            locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
            formatter = mdates.ConciseDateFormatter(locator)
            axis.xaxis.set_major_locator(locator)
            axis.xaxis.set_major_formatter(formatter)

            handles, labels = axis.get_legend_handles_labels()
            new_labels = []
            lineas = calculador.obtener_lineas(db_session)
            for l in labels:
                for linea in lineas:
                    if l == linea[0]:
                        new_labels.append(linea[1])
            axis.legend(handles, new_labels)

            axis.set_ylabel(config['ylabel'], rotation=0)
            axis.yaxis.set_label_coords(-0.1, 1.02)
            axis.set_title(config['title'])
            axis.yaxis.set_major_formatter(config['formatter'])

            for tick in axis.xaxis.get_major_ticks():
                tick.label.set_fontsize(15)
            for tick in axis.yaxis.get_major_ticks():
                tick.label.set_fontsize(15)

            axis.xaxis.label.set_size(15)
            axis.yaxis.label.set_size(15)

            axis.spines['right'].set_visible(False)
            axis.spines['top'].set_visible(False)

    return fig


***REMOVED***
    app.run()
