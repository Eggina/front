from flask import Flask, Response, render_template, request, session, _app_ctx_stack
from time import strptime, strftime
from database import db_session
from services.figures import create_figure
from services.calculador import Calculador
import secrets

***REMOVED***

app.config['SECRET_KEY'] = '1jAqXjc1hFqjas2ks5PoAw'
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
    global db_session

    calculador = Calculador()

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

    lineas = calculador.obtener_lineas(db_session)
    fechas = [x[:7]
              for x in calculador.obtener_limites_fechas_validas(db_session)]
***REMOVED***
    return render_template('home.html', indicadores=indicadores, lineas=lineas, fechas_extremas=fechas, session=session)


***REMOVED***
***REMOVED***
    global db_session
***REMOVED***
    output = create_figure(ind, db_session, session)
***REMOVED***


***REMOVED***
***REMOVED***
    db_session.remove()


***REMOVED***
    app.run()
