from flask import Flask, Response, render_template, request, session, _app_ctx_stack
***REMOVED***
from services.figures import create_figure
from services.calculador import Calculador
***REMOVED***
***REMOVED***

***REMOVED***

app.config['SECRET_KEY'] = '1jAqXjc1hFqjas2ks5PoAw'
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
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

    lineas = calculador.obtener_lineas(app.session)
***REMOVED***
        '%Y-%m') for x in calculador.obtener_limites_fechas_validas(app.session)]
***REMOVED***
***REMOVED***
    return render_template('home.html', indicadores=indicadores, lineas=lineas, fechas_extremas=fechas, session=session)


***REMOVED***
***REMOVED***
***REMOVED***
    output = create_figure(ind, app.session, session)
***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
***REMOVED***


***REMOVED***
    app.run(debug=True)
