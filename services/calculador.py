***REMOVED***
from calendar import monthrange


class Calculador:

    def __procesar_fechas(self, fecha1, fecha2):
        fecha1 = pd.to_datetime(fecha1)
        fecha2 = pd.to_datetime(fecha2)
        fecha1.replace(day=1)
        fecha2.replace(day=monthrange(fecha2.year, fecha2.month)[1])
        return fecha1, fecha2

    def __load_dataframe(self, selects, variable, tabla, fecha_inicio, fecha_final, filters, groups, session):
        fecha_inicio, fecha_final = self.__procesar_fechas(
            fecha_inicio, fecha_final)
        selects_str = 'SELECT ' + ', '.join(selects)

        config_str = ', SUM({}) AS {} FROM {} '.format(
            variable, variable, tabla)

        # fechas_str = 'WHERE fecha >= "{} 00:00:00" AND fecha <= "{} 23:59:59" '.format(
        #     fecha_inicio.strftime("%Y-%m-%d"), fecha_final.strftime("%Y-%m-%d"))

        fechas_str = 'WHERE fecha BETWEEN \'{} 00:00:00\' AND \'{} 23:59:59\' '.format(
            fecha_inicio.strftime('%Y-%m-%d'), fecha_final.strftime('%Y-%m-%d'))

        filters_str = ''
        if filters:
            for filt, values in filters.items():
                filters_str += 'AND {} IN ({}) '.format(filt,
                                                        ', '.join(values))

        groups_str = 'GROUP BY ' + ', '.join(groups)

        query = selects_str + config_str + fechas_str + \
            filters_str + groups_str + ' ORDER BY fecha'

        resoverall = session.execute(query)
        df = pd.DataFrame(resoverall.fetchall())
        df.columns = resoverall.keys()
        # df = pd.read_sql(query, session.engine)
        df['fecha'] = df['fecha'].astype('datetime64[ns, UTC]')
        return df

    def calcular_cambio_interanual(self, df, fecha_inicio, fecha_final):
        f1, f2 = self.__procesar_fechas(fecha_inicio, fecha_final)
        meses = (f2.year - f1.year)*12 + (f2.month - f1.month)
        if (meses < 12):
            return pd.DataFrame()

        if 'id_linea' in df.index.names:
            def func(df): return df.groupby(level=1)
        else:
            def func(df): return df

        variable = df.columns[-1]
        df['indicador'] = func(df[[variable]]).diff(periods=12)
        df['indicador'] = df['indicador'] / \
            (df['{}'.format(variable)] - df['indicador'])
        return df.dropna()

    def calcular_IPAX(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        return self.__load_dataframe(indexes, 'cantidad_usos', 'entrega_dggi_tarifa', fecha_inicio, fecha_final, {'id_linea': id_linea}, indexes, session).set_index(indexes)

    def calcular_IKM(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        return self.__load_dataframe(indexes, 'distancia_servicio_km', 'entrega_dist_serv_fechaok', fecha_inicio, fecha_final, {'id_linea': id_linea}, indexes, session).set_index(indexes).sort_values(indexes)

    def __calcular_xPy(self, fecha_inicio, fecha_final, id_linea, variable_x, variable_y, indexes, session):
        df_x = self.__load_dataframe(
            indexes, variable_x['nombre'], variable_x['tabla'], fecha_inicio, fecha_final, variable_x['filters'], indexes, session)
        df_x = df_x.set_index(indexes)

        df_y = self.__load_dataframe(
            indexes, variable_y['nombre'], variable_y['tabla'], fecha_inicio, fecha_final, variable_y['filters'], indexes, session)
        df_y = df_y.set_index(indexes)

        if variable_x['nombre'] == variable_y['nombre']:
            variable_x['nombre'] = variable_x['nombre'] + '_x'
            variable_y['nombre'] = variable_y['nombre'] + '_y'

        df_xy = df_x.join(df_y, lsuffix='_x', rsuffix='_y')
        df_xy['indicador'] = df_xy[variable_x['nombre']] / \
            df_xy[variable_y['nombre']]
        return df_xy

    def calcular_IPK(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        variable_x = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        variable_y = {'nombre': 'distancia_servicio_km',
                      'tabla': 'entrega_dist_serv_fechaok', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, indexes, session)
        return df.rename(columns={'indicador': 'ipk'})

    def calcular_RPK(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        variable_x = {'nombre': 'monto', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea}}
        variable_y = {'nombre': 'distancia_servicio_km',
                      'tabla': 'entrega_dist_serv_fechaok', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, indexes, session)
        return df.rename(columns={'indicador': 'rpk'})

    def calcular_ITM(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        variable_x = {'nombre': 'monto', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea}}
        variable_y = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        df = self.__calcular_xPy(
            fecha_inicio, fecha_final, id_linea, variable_x, variable_y, indexes, session)
        return df.rename(columns={'indicador': 'itm'})

    def calcular_IRT(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        df = self.calcular_ITM(fecha_inicio, fecha_final,
                               id_linea, indexes, session)

        tarifas = self.__load_dataframe(
            ['fecha'], 'valor', 'tarifa_plana', fecha_inicio, fecha_final, None, ['fecha'], session)
        tarifas = tarifas.set_index('fecha')
        ind = df.index.get_level_values('fecha')

        df['tp'] = tarifas.loc[ind].values

        df['irt'] = df['itm']/df['tp']
        return df

    def __calcular_AT(self, fecha_inicio, fecha_final, id_linea, indexes, contratos, session):
        variable_x = {'nombre': 'cantidad_usos', 'tabla': 'entrega_dggi_tarifa', 'filters': {
            'id_linea': id_linea, 'contrato': contratos}}
        variable_y = {'nombre': 'cantidad_usos',
                      'tabla': 'entrega_dggi_tarifa', 'filters': {'id_linea': id_linea}}
        return self.__calcular_xPy(fecha_inicio, fecha_final, id_linea, variable_x, variable_y, indexes, session)

    def calcular_AT_Nac(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, indexes, ['\'621\''], session)
        return df.rename(columns={'indicador': 'at_nac'})

    def calcular_AT_Loc(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        contratos = ['\'{}\''.format(x) for x in range(521, 532)]
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, indexes, contratos, session)
        return df.rename(columns={'indicador': 'at_loc'})

    def calcular_T_Plana(self, fecha_inicio, fecha_final, id_linea, indexes, session):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                id_linea, indexes, ['\'602\''], session)
        return df.rename(columns={'indicador': 't_plana'})

    def obtener_limites_fechas_validas(self, session):
        query = 'SELECT MIN(FECHA) AS fecha_min, MAX(FECHA) AS fecha_max FROM entrega_dggi_tarifa'
        resoverall = session.execute(query)
        df = pd.DataFrame(resoverall.fetchall())
        # pd.read_sql('SELECT MIN(FECHA) AS fecha_min, MAX(FECHA) AS fecha_max FROM entrega_dggi_tarifa', session.engine).values[0]
        return df.values[0]

    def obtener_lineas(self, session):
        query = 'SELECT id_linea, linea FROM lineas'
        resoverall = session.execute(query)
        df = pd.DataFrame(resoverall.fetchall())
        # pd.read_sql('SELECT id_linea, linea FROM lineas', session.engine).values
        return df.values


def setup_indicadores(indicadores):
    calculador = Calculador()
    indicadores['ipax']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_IPAX(
        a0, a1, a2, a3, a4)
    indicadores['ikm']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_IKM(
        a0, a1, a2, a3, a4)
    indicadores['ipk']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_IPK(
        a0, a1, a2, a3, a4)
    indicadores['rpk']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_RPK(
        a0, a1, a2, a3, a4)
    indicadores['itm']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_ITM(
        a0, a1, a2, a3, a4)
    indicadores['irt']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_IRT(
        a0, a1, a2, a3, a4)
    indicadores['ianac']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_AT_Nac(
        a0, a1, a2, a3, a4)
    indicadores['ialoc']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_AT_Loc(
        a0, a1, a2, a3, a4)
    indicadores['itp']['fun'] = lambda a0, a1, a2, a3, a4: calculador.calcular_T_Plana(
        a0, a1, a2, a3, a4)
    return indicadores
