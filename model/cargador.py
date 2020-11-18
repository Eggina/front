***REMOVED***
import re
***REMOVED***


class Cargador:

    def cargar_tablas(self, files):
        tables = dict()
        for f in files:
            match1 = re.search(r'\d+_', f)
            match2 = re.search(r'_\S+.csv', f)
            if match1 is not None and match2 is not None:
                year = match1.group()[:-1]
                name = match2.group()[1:-4]

                if not year in tables:
                    tables[year] = dict()
                # tables[year][name] = pd.read_csv(
                #     'gs://' + f, sep=';', decimal=",")
                tables[year][name] = pd.read_csv(
                    './data/{}'.format(f), sep=';', decimal=','
                )
        return tables


***REMOVED***
    cargador = Cargador()
    files = os.listdir('./data/')
    tables = cargador.cargar_tablas(files)
    print(tables['2018']['Entrega_Dist_Serv_FechaOk'].head())
