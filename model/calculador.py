***REMOVED***
import re
***REMOVED***
import numpy as np
from model.cargador import Cargador
from calendar import monthrange


class Calculador:

    def setear_tablas(self, tablas):
        self.tablas = tablas
        for key, table in self.tablas.items():
            table['Entrega_Dist_Serv_FechaOk']['FECHA_INI'] = pd.to_datetime(
                table['Entrega_Dist_Serv_FechaOk']['FECHA_INI'], dayfirst=True)
            table['Entrega_Dist_Serv_FechaOk']['MES'] = table['Entrega_Dist_Serv_FechaOk']['FECHA_INI'].dt.month
            table['Entrega_Dist_Serv_FechaOk']['FECHA'] = pd.to_datetime(
                table['Entrega_Dist_Serv_FechaOk']['FECHA_INI'].apply(lambda x: x.strftime('%Y-%m')))
            table['Entrega_Dist_Serv_FechaOk'] = table['Entrega_Dist_Serv_FechaOk'].rename(
                columns={'LINEA': 'ID_LINEA'})
            table['Entrega_dggi_tarifa']['FECHA'] = pd.to_datetime(
                table['Entrega_dggi_tarifa']['MES'].astype(str)+'/'+table['Entrega_dggi_tarifa']['AÑO'].astype(str))
            table['Tarifa_plana']['FECHA'] = pd.to_datetime(
                table['Tarifa_plana']['FECHA'])
            table['Tarifa_plana'] = table['Tarifa_plana'].set_index('FECHA')

        self.años = list(self.tablas.keys())
        self.años.sort()

    def __agrupar_agregar(self, tabla, grupo, var, fun):
        return tabla[grupo+var].groupby(by=grupo).agg(fun)

    def __unir(self, tablas):
        return tablas[0].join(tablas[1])

    def __procesar(self, tabla, nivel0, nivel1, agregar_niveles):
        if agregar_niveles[1]:
            if agregar_niveles[0]:
                return pd.DataFrame(tabla.loc(axis=0)[(nivel0, nivel1)].sum()).transpose()
            else:
                return tabla.loc(axis=0)[(nivel0, nivel1)].groupby(level=0).sum()
        else:
            if agregar_niveles[0]:
                return tabla.loc(axis=0)[(nivel0, nivel1)].groupby(level=1).sum()
        return tabla.loc(axis=0)[(nivel0, nivel1)]

    def obtener_fecha_mas_temprana(self):
        fecha = []
        for año, tabla in self.tablas.items():
            fecha.append(tabla['Entrega_dggi_tarifa']['FECHA'].min())
        return np.min(fecha)

    def obtener_fecha_mas_tardia(self):
        fecha = []
        for año, tabla in self.tablas.items():
            fecha.append(tabla['Entrega_dggi_tarifa']['FECHA'].max())
        return np.max(fecha)

    def __calcular_Ix(self, fecha_inicio, fecha_final, idlinea, agregar_lineas, variable):
        fecha_inicio, fecha_final, años = self.__procesar_fechas(
            fecha_inicio, fecha_final)

        meses = (fecha_final.year - fecha_inicio.year)*12 + \
            (fecha_final.month - fecha_inicio.month)

        if (meses < 12):
            return pd.DataFrame()

        df = pd.concat([self.__agrupar_agregar(self.tablas[str(año)][variable['tabla']], [
                       'FECHA', 'ID_LINEA'], [variable['nombre']], variable['fun']) for año in años])

        df = self.__procesar(
            df, slice(fecha_inicio, fecha_final), idlinea, [False, agregar_lineas])

        if agregar_lineas:
            df['indicador'] = df.diff(periods=12)
        else:
            df['indicador'] = df.groupby(level=1).diff(periods=12)

        df['indicador'] = df['indicador'] / \
            (df[variable['nombre']] - df['indicador'])
        return df.dropna()

    def calcular_IPAX(self, fecha_inicio, fecha_final, idlinea, agregar_lineas=False):
        pax = self.__calcular_Ix(fecha_inicio, fecha_final, idlinea, agregar_lineas, {
            'tabla': 'Entrega_dggi_tarifa', 'nombre': 'CANTIDAD_USOS', 'fun': 'sum'})
        pax = pax.rename(columns={'indicador': 'ipax'})
        return pax

    def calcular_IKM(self, fecha_inicio, fecha_final, idlinea, agregar_lineas=False):
        km = self.__calcular_Ix(fecha_inicio, fecha_final, idlinea, agregar_lineas, {
            'tabla': 'Entrega_Dist_Serv_FechaOk', 'nombre': 'DISTANCIA_SERVICIO_KM', 'fun': 'sum'})
        km = km.rename(columns={'indicador': 'ikm'})
        return km

    def __procesar_fechas(self, fecha1, fecha2):
        fecha1 = pd.to_datetime(fecha1)
        fecha2 = pd.to_datetime(fecha2)
        fecha1.replace(day=1)
        fecha2.replace(day=monthrange(fecha2.year, fecha2.month)[1])
        años = range(fecha1.year, fecha2.year + 1)
        return fecha1, fecha2, años

    def __calcular_XPK(self, fecha_inicio, fecha_final, idlinea, variable, agregar_lineas):
        fecha_inicio, fecha_final, años = self.__procesar_fechas(
            fecha_inicio, fecha_final)

        df = pd.concat([self.__agrupar_agregar(self.tablas[str(año)]['Entrega_dggi_tarifa'], ['FECHA', 'ID_LINEA'], [
            variable], 'sum') for año in años])

        km = pd.concat([self.__agrupar_agregar(self.tablas[str(año)]['Entrega_Dist_Serv_FechaOk'], ['FECHA', 'ID_LINEA'], [
            'DISTANCIA_SERVICIO_KM'], 'sum') for año in años])

        df_km = self.__procesar(self.__unir([df, km]), slice(
            fecha_inicio, fecha_final), idlinea, [False, agregar_lineas])

        df_km['indicador'] = df_km[variable]/df_km['DISTANCIA_SERVICIO_KM']
        return df_km

    def calcular_IPK(self, fecha_inicio, fecha_final, idlinea, agregar_lineas=False):
        pax_km = self.__calcular_XPK(
            fecha_inicio, fecha_final, idlinea, 'CANTIDAD_USOS', agregar_lineas)
        pax_km = pax_km.rename(columns={'indicador': 'ipk'})
        return pax_km

    def calcular_RPK(self, fecha_inicio, fecha_final, idlinea, agregar_lineas=False):
        pax_km = self.__calcular_XPK(
            fecha_inicio, fecha_final, idlinea, 'MONTO', agregar_lineas)
        pax_km = pax_km.rename(columns={'indicador': 'rpk'})
        return pax_km

    def calcular_ITM(self, fecha_inicio, fecha_final, idlinea, agregar_lineas=False):
        fecha_inicio, fecha_final, años = self.__procesar_fechas(
            fecha_inicio, fecha_final)

        df = pd.concat([self.__agrupar_agregar(self.tablas[str(año)]['Entrega_dggi_tarifa'], [
            'FECHA', 'ID_LINEA'], ['CANTIDAD_USOS', 'MONTO'], 'sum') for año in años])
        df = self.__procesar(df, slice(fecha_inicio, fecha_final), idlinea, [
            False, agregar_lineas])
        df['itm'] = df['MONTO']/df['CANTIDAD_USOS']
        return df

    def calcular_IRT(self, fecha_inicio, fecha_final, idlinea, agregar_lineas):
        df = self.calcular_ITM(fecha_inicio, fecha_final,
                               idlinea, agregar_lineas)

        fecha_inicio, fecha_final, años = self.__procesar_fechas(
            fecha_inicio, fecha_final)
        tarifas = pd.concat(
            [self.tablas[str(año)]['Tarifa_plana'] for año in años])

        tp = df.index.get_level_values('FECHA')

        df['Tarifa_plana'] = tarifas.loc[tp].values

        df['irt'] = df['itm']/df['Tarifa_plana']
        return df

    def __calcular_AT(self, fecha_inicio, fecha_final, idlinea, agregar_lineas, contratos):
        fecha_inicio, fecha_final, años = self.__procesar_fechas(
            fecha_inicio, fecha_final)

        df1 = pd.concat([self.__agrupar_agregar(self.tablas[str(año)]['Entrega_dggi_tarifa'], [
            'FECHA', 'ID_LINEA'], ['CANTIDAD_USOS'], 'sum') for año in años])
        df2 = pd.concat([self.__agrupar_agregar(self.tablas[str(año)]['Entrega_dggi_tarifa'], [
            'FECHA', 'ID_LINEA', 'CONTRATO'], ['CANTIDAD_USOS'], 'sum') for año in años])

        df2 = df2.loc[(slice(None), slice(None), contratos)]
        df2 = self.__agrupar_agregar(df2.reset_index(), ['FECHA', 'ID_LINEA'], [
            'CANTIDAD_USOS'], 'sum')
        df2 = df2.rename(columns={'CANTIDAD_USOS': 'CANTIDAD_USOS_AT'})

        df = self.__unir([df1, df2])
        df = self.__procesar(df, slice(fecha_inicio, fecha_final), idlinea, [
            False, agregar_lineas])

        df['indicador'] = df['CANTIDAD_USOS_AT']/df['CANTIDAD_USOS']
        return df

    def calcular_AT_Nac(self, fecha_inicio, fecha_final, idlinea, agregar_lineas):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                idlinea, agregar_lineas, 621)
        df = df.rename(columns={'indicador': 'at_nac'})
        return df

    def calcular_AT_Loc(self, fecha_inicio, fecha_final, idlinea, agregar_lineas):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                idlinea, agregar_lineas, slice(521, 531))
        df = df.rename(columns={'indicador': 'at_loc'})
        return df

    def calcular_T_Plana(self, fecha_inicio, fecha_final, idlinea, agregar_lineas):
        df = self.__calcular_AT(fecha_inicio, fecha_final,
                                idlinea, agregar_lineas, 602)
        df = df.rename(columns={'indicador': 't_plana'})
        return df


***REMOVED***
    cdor = Cargador()
    files = os.listdir('./data/')
    tables = cdor.cargar_tablas(files)
    calculador = Calculador()
    calculador.setear_tablas(tables)
    calculador.calcular_IPAX(['2018', '2019'], [1, 2, 3, 4, 5], [
                             1224, 1226], False, False)
    calculador.calcular_IPAX(['2018', '2019'], [1, 2, 3, 4, 5], [
                             1224, 1226], False, True)
    calculador.calcular_IPAX(['2018', '2019'], [1, 2, 3, 4, 5], [
                             1224, 1226], True, False)
    calculador.calcular_IPAX(['2018', '2019'], [1, 2, 3, 4, 5], [
                             1224, 1226], True, True)
    calculador.calcular_IKM(['2018', '2019'], [1, 2, 3, 4, 5], [
        1224, 1226], False, False)
    calculador.calcular_IKM(['2018', '2019'], [1, 2, 3, 4, 5], [
        1224, 1226], False, True)
    calculador.calcular_IKM(['2018', '2019'], [1, 2, 3, 4, 5], [
        1224, 1226], True, False)
    calculador.calcular_IKM(['2018', '2019'], [1, 2, 3, 4, 5], [
        1224, 1226], True, True)
    calculador.calcular_IPK('2018-01-01', '2019-12-31', [1226, 1227], False)
    calculador.calcular_IRT('2018-01-01', '2019-12-31', [1225], False)
    calculador.calcular_AT_Nac('2018-01-01', '2019-12-31', [1225], False)
    calculador.calcular_AT_Loc('2018-01-01', '2019-12-31', [1225], False)
    calculador.calcular_T_Plana('2018-01-01', '2019-12-31', [1225], False)
