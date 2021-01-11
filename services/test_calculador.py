from calculador import Calculador
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

***REMOVED***
    calc = Calculador()
    SQLALCHEMY_DATABASE_URL = 'postgresql://read_only_datos_sube:sudoku@localhost:5432/datos_sube'
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
    f1, f2 = ('2018-01', '2019-12')

    indexes = ['fecha']
    id_linea = ['\'1225\'', '\'1233\'']

    df = calc.calcular_IPAX(f1, f2, id_linea, indexes, session)
    print(df)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_IKM(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_IPK(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_RPK(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_ITM(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_IRT(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_AT_Nac(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_AT_Loc(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.calcular_T_Plana(f1, f2, id_linea, indexes, session)
    print(calc.calcular_cambio_interanual(df, f1, f2))
    df = calc.obtener_limites_fechas_validas(session)
    df = calc.obtener_lineas(session)
