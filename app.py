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
from cargador import Cargador
from calculador import Calculador


class Main:
    def setear_cargador(self, cargador):
        self.cargador = cargador

    def setear_tablas(self, tablas):
        self.tablas = tablas

    def setear_calculador(self, calculador):
        self.calculador = calculador
        self.calculador.setear_tablas(self.tablas)


***REMOVED***

app.config['SECRET_KEY'] = "some_random"
***REMOVED***
***REMOVED***

script_dir = os.path.dirname(__file__)
rel_path = 'data'

main = Main()
main.setear_cargador(Cargador())
main.setear_tablas(main.cargador.cargar_tablas(
    os.path.join(script_dir, rel_path)))
main.setear_calculador(Calculador())


***REMOVED***
***REMOVED***
***REMOVED***
        session['idlineas'] = [int(id)
                               for id in request.form.getlist('lineas')]
***REMOVED***
        session['inicio'] = request.form.getlist('inicio')
        session['fin'] = request.form.getlist('fin')
        session['año'] = request.form.getlist('año')
        print(session)

    return render_template('home.html', main=main)


@app.route('/plot/<ind>')
***REMOVED***
    fig = create_figure(ind)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
***REMOVED***


def create_figure(ind):
    fig = Figure(figsize=(8.09, 5), tight_layout=True)
    axis = fig.add_subplot(1, 1, 1)

    if session.get('idlineas') is not None:
        table = pd.DataFrame()

        if ind == 'ipax':
            table = main.calculador.calcular_IPAX(main.calculador.obtener_año_anterior(session['año'][0]), np.arange(
                1, 13), session.get('idlineas'), False, 'agregadas' in session.get('config')).reset_index()
        if ind == 'ikm':
            table = main.calculador.calcular_IKM(main.calculador.obtener_año_anterior(session['año'][0]), np.arange(
                1, 13), session.get('idlineas'), False, 'agregadas' in session.get('config')).reset_index()
        if ind == 'ipk':
            table = main.calculador.calcular_IPK(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'rpk':
            table = main.calculador.calcular_RPK(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'itm':
            table = main.calculador.calcular_ITM(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'irt':
            table = main.calculador.calcular_IRT(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'at_nac':
            table = main.calculador.calcular_AT_Nac(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 'at_loc':
            table = main.calculador.calcular_AT_Loc(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
                'idlineas'), 'agregadas' in session.get('config')).reset_index()
        if ind == 't_plana':
            table = main.calculador.calcular_T_Plana(session['inicio'][0]+'-01', session['fin'][0]+'-31', session.get(
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
                    main.calculador.tablas['2018']['Lineas'].loc[main.calculador.tablas['2018']['Lineas']['ID_LINEA'] == int(l)]['NOMBRE'].iloc[0])
            axis.legend(handles, new_labels)

            axis.set_ylabel(axis.yaxis.get_label().get_text().upper())

            for tick in axis.xaxis.get_major_ticks():
                tick.label.set_fontsize(15)
            for tick in axis.yaxis.get_major_ticks():
                tick.label.set_fontsize(15)

            axis.xaxis.label.set_size(15)
            axis.yaxis.label.set_size(15)

    return fig
