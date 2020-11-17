***REMOVED***
import re
***REMOVED***


class Cargador:

    def cargar_tablas(self, uri):
        files = [f for f in os.listdir(
            uri) if os.path.isfile(os.path.join(uri, f))]
        tables = dict()
        for f in files:
            match1 = re.search(r'\d+_', f)
            match2 = re.search(r'_\S+.csv', f)
            if match1 is not None and match2 is not None:
                year = f[:match1.end()-1]
                name = f[match2.start()+1:-4]

                if not year in tables:
                    tables[year] = dict()
                print(match2.group())
                tables[year][name] = pd.read_csv(os.path.join(
                    uri, '{}_{}.csv'.format(year, name)), sep=';', decimal=",")
        return tables


***REMOVED***
    cargador = Cargador()
    script_dir = os.path.dirname(__file__)
    rel_path = 'data'
    tables = cargador.cargar_tablas(os.path.join(script_dir, rel_path))
    print(tables['2018']['Entrega_Dist_Serv_FechaOk'].head())
