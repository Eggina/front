import io
***REMOVED***
import sys
import random
from flask import Flask, Response, render_template, request, session
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import ticker as mticker
from matplotlib import pyplot as plt
from matplotlib import dates as mdates

from time import strptime, strftime
import numpy as np
***REMOVED***
import seaborn as sns
from model.cargador import Cargador
from model.calculador import Calculador


***REMOVED***

app.config['SECRET_KEY'] = "some_random"
***REMOVED***
***REMOVED***


class Director():

    def setear_cargador(self, cargador):
        self.cargador = cargador

    def setear_tablas(self, tablas):
        self.tablas = tablas

    def setear_calculador(self, calculador):
        self.calculador = calculador
        self.calculador.setear_tablas(self.tablas)


***REMOVED***
***REMOVED***

    # fs = gcsfs.GCSFileSystem()
    # files = fs.ls(os.environ['FILES_PATH'])

    files = os.listdir('./data/')

    director = Director()
    director.setear_cargador(Cargador())
    director.setear_tablas(director.cargador.cargar_tablas(files))
    director.setear_calculador(Calculador())

***REMOVED***
        session['idlineas'] = [int(id)
                               for id in request.form.getlist('lineas')]
***REMOVED***
        session['inicio'] = request.form.getlist('inicio')
        session['fin'] = request.form.getlist('fin')
        print(session)

    return render_template('home.html', director=director, session=session)


@app.route('/plot/<ind>')
***REMOVED***
    fig = create_figure(ind)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
***REMOVED***


def create_figure(ind):

    # fs = gcsfs.GCSFileSystem()
    # files = fs.ls(os.environ['FILES_PATH'])

    fig = Figure(figsize=(8.09, 5), tight_layout=True)
    axis = fig.add_subplot(1, 1, 1)

    if session.get('idlineas'):
        files = os.listdir('./data/')

        director = Director()
        director.setear_cargador(Cargador())
        director.setear_tablas(director.cargador.cargar_tablas(files))
        director.setear_calculador(Calculador())

        table = pd.DataFrame()

        if ind == 'ipax':
            table = director.calculador.calcular_IPAX(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'ikm':
            table = director.calculador.calcular_IKM(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'ipk':
            table = director.calculador.calcular_IPK(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'rpk':
            table = director.calculador.calcular_RPK(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'itm':
            table = director.calculador.calcular_ITM(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'irt':
            table = director.calculador.calcular_IRT(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'at_nac':
            table = director.calculador.calcular_AT_Nac(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'at_loc':
            table = director.calculador.calcular_AT_Loc(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 't_plana':
            table = director.calculador.calcular_T_Plana(session['inicio'][0], session['fin'][0], session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()

        if not table.empty:
            custom_palette = sns.color_palette("Paired", len(session.get(
                'idlineas')))

            if not 'agregadas' in session.get('config') and not 'agrupadas' in session.get('config'):
                sns.lineplot(x=table.columns[0], y=table.columns[-1],
                             data=table, hue=table.columns[1], ax=axis, legend="full", palette=custom_palette)
            else:
                sns.lineplot(
                    x=table.columns[0], y=table.columns[-1], data=table, ax=axis, legend="full", palette=custom_palette)

            if 'MES' in table.columns:
                axis.xaxis.set_major_locator(mticker.MultipleLocator(3))
                axis.xaxis.set_minor_locator(mticker.MultipleLocator(1))
                axis.xaxis.set_major_formatter(mticker.FuncFormatter(
                    lambda x, pos: '0' if (x < 1 or x > 12) else strftime('%b', strptime(str(int(x)), '%m'))))

            if 'FECHA' in table.columns:
                locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
                formatter = mdates.ConciseDateFormatter(locator)
                axis.xaxis.set_major_locator(locator)
                axis.xaxis.set_major_formatter(formatter)

            handles, labels = axis.get_legend_handles_labels()
            new_labels = []
            for l in labels:
                new_labels.append(
                    director.calculador.tablas['2018']['Lineas'].loc[director.calculador.tablas['2018']['Lineas']['ID_LINEA'] == int(l)]['NOMBRE'].iloc[0])
            axis.legend(handles, new_labels)

            axis.set_ylabel(axis.yaxis.get_label().get_text().upper())

            for tick in axis.xaxis.get_major_ticks():
                tick.label.set_fontsize(15)
            for tick in axis.yaxis.get_major_ticks():
                tick.label.set_fontsize(15)

            axis.xaxis.label.set_size(15)
            axis.yaxis.label.set_size(15)

    return fig


***REMOVED***
    app.run(debug=True)
