import io
***REMOVED***
import seaborn as sns
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from .calculador import Calculador


def setup_indicadores(indicadores):
    indicadores['ipax']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:,}'.format(int(x)).replace(',', '.'))
    indicadores['ikm']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:,}'.format(int(x)).replace(',', '.'))
    indicadores['ipk']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.3f}'.format(x))
    indicadores['rpk']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.2f}'.format(x))
    indicadores['itm']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.2f}'.format(x))
    indicadores['irt']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.1f}'.format(100*x))
    indicadores['ianac']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.1f}'.format(100*x))
    indicadores['ialoc']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.1f}'.format(100*x))
    indicadores['itp']['formatter'] = mticker.FuncFormatter(
        lambda x, pos: '{:.1f}'.format(100*x))
    return indicadores


def create_figure(ind, db_session, session, indicadores):

    fig = Figure(figsize=(10, 5), tight_layout=True)
    axis = fig.add_subplot(1, 1, 1)

    calculador = Calculador()

    if session.get('id_lineas'):

        table = pd.DataFrame()

        id_lineas = session.get('id_lineas')
        id_lineas = ['\'{}\''.format(x) for x in id_lineas]

        config = dict()
        config['title'] = ''
        config['ylabel'] = ''
        config['formatter'] = None

        if 'agregadas' in session.get('config'):
            indexes = ['fecha']
        else:
            indexes = ['fecha', 'id_linea']

        table = indicadores[ind]['fun'](
            session['fecha']['inicio'][0], session['fecha']['fin'][0], id_lineas, indexes, db_session)
        config['title'] = indicadores[ind]['title']
        config['ylabel'] = indicadores[ind]['ylabel']
        config['formatter'] = indicadores[ind]['formatter']
        config['alarm1'] = indicadores[ind]['alarm1']
        config['alarm2'] = indicadores[ind]['alarm2']
        config['ylim'] = indicadores[ind]['ylim']
        config['alarm1_enable'] = indicadores[ind]['alarm1_enable']
        config['alarm2_enable'] = indicadores[ind]['alarm2_enable']

        if 'cambio' in session['indicadores'][ind]:
            table = calculador.calcular_cambio_interanual(
                table, session['fecha']['inicio'][0], session['fecha']['fin'][0]).reset_index()
            config['title'] = indicadores[ind]['alt_title']
            config['ylabel'] = '%'
            config['formatter'] = mticker.FuncFormatter(
                lambda x, pos: '{:.1f}'.format(100*x))
            config['alarm1'] = indicadores[ind]['alt_alarm1']
            config['alarm2'] = indicadores[ind]['alt_alarm2']
            config['ylim'] = indicadores[ind]['alt_ylim']
            config['alarm1_enable'] = indicadores[ind]['alt_alarm1_enable']
            config['alarm2_enable'] = indicadores[ind]['alt_alarm2_enable']
        else:
            table = table.reset_index()

        if not table.empty:
            custom_palette = sns.color_palette(
                "Paired", len(session.get('id_lineas')))

            if not 'agregadas' in session.get('config') and not 'agrupadas' in session.get('config'):
                sns.lineplot(x=table.columns[0], y=table.columns[-1],
                             data=table, hue=table.columns[1], ax=axis, legend="full", palette=custom_palette, marker='o')
            else:
                sns.lineplot(
                    x=table.columns[0], y=table.columns[-1], data=table, ax=axis, legend="full", palette=custom_palette, marker='o')

            if config['ylim'][0] < config['ylim'][1]:
                axis.set_ylim(config['ylim'])

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

            ylims = axis.get_ylim()

            if config['alarm1_enable'] != 0:
                alarm1 = [0, 0]
                alarm1[0] = ylims[0] if ylims[0] > config['alarm1'][0] else ylims[1] if ylims[1] < config['alarm1'][0] else config['alarm1'][0]
                alarm1[1] = ylims[1] if ylims[1] < config['alarm1'][1] else ylims[0] if ylims[0] > config['alarm1'][1] else config['alarm1'][1]
                axis.axhspan(alarm1[0], alarm1[1], facecolor='g', alpha=0.125)
            if config['alarm2_enable'] != 0:
                alarm2 = [0, 0]
                alarm2[0] = ylims[0] if ylims[0] > config['alarm2'][0] else ylims[1] if ylims[1] < config['alarm2'][0] else config['alarm2'][0]
                alarm2[1] = ylims[1] if ylims[1] < config['alarm2'][1] else ylims[0] if ylims[0] > config['alarm2'][1] else config['alarm2'][1]
                axis.axhspan(alarm2[0], alarm2[1], facecolor='r', alpha=0.125)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output
