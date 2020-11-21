***REMOVED***
from calendar import monthrange


class Calculador:

    def __procesar_fechas(self, fecha1, fecha2):
        fecha1 = pd.to_datetime(fecha1)
        fecha2 = pd.to_datetime(fecha2)
        fecha1.replace(day=1)
        fecha2.replace(day=monthrange(fecha2.year, fecha2.month)[1])
        return fecha1, fecha2

    def __load_dataframe(self, selects, variable, tabla, fecha_inicio, fecha_final, filters, groups, db):
        fecha_inicio, fecha_final = self.__procesar_fechas(
            fecha_inicio, fecha_final)
        selects_str = 'SELECT ' + ', '.join(selects)

        config_str = ', SUM({}) AS {} FROM {} '.format(
            variable, variable, tabla)

        fechas_str = 'WHERE fecha >= "{} 00:00:00" AND fecha <= "{} 23:59:59" '.format(
            fecha_inicio.strftime("%Y-%m-%d"), fecha_final.strftime("%Y-%m-%d"))

        filters_str = ''
        if filters:
            for filt, values in filters.items():
                filters_str += 'AND {} IN ({}) '.format(filt,
                                                        ', '.join(values))

        groups_str = 'GROUP BY ' + ', '.join(groups)

        query = selects_str + config_str + fechas_str + filters_str + groups_str
        df = pd.read_sql(query, db.engine)
        df['fecha'] = df['fecha'].astype('datetime64[ns, UTC]')
        return df

    def __calcular_Ix(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, variable, db):
        f1, f2 = self.__procesar_fechas(
            fecha_inicio, fecha_final)
        meses = (f2.year - f1.year)*12 + (f2.month - f1.month)
        if (meses < 12):
            return pd.DataFrame()

        if agregar_lineas:
            var_list = ['fecha']
            def func(df): return df
        else:
            var_list = ['fecha', 'id_linea']
            def func(df): return df.groupby(level=1)

        df = self.__load_dataframe(var_list, variable['nombre'], variable['tabla'], fecha_inicio, fecha_final, {
                                   'id_linea': id_linea}, var_list, db)
        df = df.set_index(var_list)
        df['indicador'] = func(df).diff(periods=12)

        df['indicador'] = df['indicador'] / \
            (df['{}'.format(variable['nombre'])] - df['indicador'])
        return df.dropna()

    def calcular_IPAX(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        df = self.__calcular_Ix(fecha_inicio, fecha_final, id_linea, agregar_lineas, {
            'tabla': 'entrega_dggi_tarifa', 'nombre': 'cantidad_usos'}, db)
        return df.rename(columns={'indicador': 'ipax'})

    def calcular_IKM(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        df = self.__calcular_Ix(fecha_inicio, fecha_final, id_linea, agregar_lineas, {
                                'tabla': 'entrega_dist_serv_fechaok', 'nombre': 'distancia_servicio_km'}, db)
        return df.rename(columns={'indicador': 'ikm'})

    def __calcular_xPy(self, fecha_inicio, fecha_final, id_linea, variable_x, variable_y, agregar_lineas, db):
        if agregar_lineas:
            var_list = ['fecha']
        else:
            var_list = ['fecha', 'id_linea']

        df_x = self.__load_dataframe(
            var_list, variable_x['nombre'], variable_x['tabla'], fecha_inicio, fecha_final, variable_x['filters'], var_list, db)
        df_x = df_x.set_index(var_list)

        df_y = self.__load_dataframe(
            var_list, variable_y['nombre'], variable_y['tabla'], fecha_inicio, fecha_final, variable_y['filters'], var_list, db)
        df_y = df_y.set_index(var_list)

        if variable_x['nombre'] == variable_y['nombre']:
            variable_x['nombre'] = variable_x['nombre'] + '_x'
            variable_y['nombre'] = variable_y['nombre'] + '_y'

        df_xy = df_x.join(df_y, lsuffix='_x', rsuffix='_y')
        df_xy['indicador'] = df_xy[variable_x['nombre']] / \
            df_xy[variable_y['nombre']]
        return df_xy

    def calcular_IPK(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        variable_x = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        variable_y = {'nombre': 'distancia_servicio_km',
                      'tabla': 'entrega_dist_serv_fechaok', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, agregar_lineas, db)
        return df.rename(columns={'indicador': 'ipk'})

    def calcular_RPK(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        variable_x = {'nombre': 'monto', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea}}
        variable_y = {'nombre': 'distancia_servicio_km',
                      'tabla': 'entrega_dist_serv_fechaok', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, agregar_lineas, db)
        return df.rename(columns={'indicador': 'rpk'})

    def calcular_ITM(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        variable_x = {'nombre': 'monto', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea}}
        variable_y = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, agregar_lineas, db)
        return df.rename(columns={'indicador': 'itm'})

    def calcular_IRT(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        df = self.calcular_ITM(fecha_inicio, fecha_final,
                               id_linea, agregar_lineas, db)

        tarifas = self.__load_dataframe(
            ['fecha'], 'valor', 'tarifa_plana', fecha_inicio, fecha_final, None, ['fecha'], db)
        tarifas = tarifas.set_index('fecha')
        ind = df.index.get_level_values('fecha')

        df['tp'] = tarifas.loc[ind].values

        df['irt'] = df['itm']/df['tp']
        return df

    def __calcular_AT(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, contratos, db):
        variable_x = {'nombre': 'cantidad_usos', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea, 'contrato': contratos}}
        variable_y = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        return self.__calcular_xPy(fecha_inicio, fecha_final, id_linea, variable_x, variable_y, agregar_lineas, db)

    def calcular_AT_Nac(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, agregar_lineas, ['\"621\"'], db)
        return df.rename(columns={'indicador': 'at_nac'})

    def calcular_AT_Loc(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        contratos = ['\"{}\"'.format(x) for x in range(521, 532)]
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, agregar_lineas, contratos, db)
        return df.rename(columns={'indicador': 'at_loc'})

    def calcular_T_Plana(self, fecha_inicio, fecha_final, id_linea, agregar_lineas, db):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, agregar_lineas, ['\"602\"'], db)
        return df.rename(columns={'indicador': 't_plana'})

    def obtener_limites_fechas_validas(self, db):
        return pd.read_sql('SELECT MIN(FECHA) AS fecha_min, MAX(FECHA) AS fecha_max FROM entrega_dggi_tarifa', db.engine).values[0]

    def obtener_lineas(self, db):
        return pd.read_sql('SELECT id_linea, linea FROM lineas', db.engine).values


***REMOVED***
    calc = Calculador()
    db = DataBase()
    db.create_engine('sqlite:///data.db')
    f1, f2 = ('2018-01', '2019-12')

    agregar_lineas = True
    id_linea = ['\"1225\"', '\"1233\"']

    # print(calc.calcular_IPAX(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_IKM(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_IPK(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_RPK(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_ITM(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_IRT(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_AT_Nac(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_AT_Loc(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.calcular_T_Plana(f1, f2, id_linea, agregar_lineas, db))
    # print(calc.obtener_limites_fechas_validas(db))
    # print(calc.obtener_lineas(db))