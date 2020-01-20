import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import datetime
import re
import math
import sys
import pytz
import numpy

delimiters = "'",",","\n"
regexPattern = '|'.join(map(re.escape, delimiters))
control_down = False
alt_down = False

class Datos:
    def __init__(self, descartar=False, altura=0.0, date="2018-01-1 00:00:00"):
        self.descartar = descartar
        self.altura = float(altura)
        deli = ".","\n"
        fecha = re.split('|'.join(map(re.escape, deli)),date)
        self.date = datetime.datetime.strptime(fecha[0], '%Y-%m-%d %H:%M:%S')

def arreglarDatosaTramosEinsertar(indiceOrigen, indiceDestino):
    lineadonde = re.split(regexPattern, fileTextA[indiceDestino])
    lineaque = re.split(regexPattern, fileText[indiceOrigen])
    tiempodonde= datetime.datetime.strptime(lineadonde[1], '%Y-%m-%d %H:%M:%S')
    tiempoque = datetime.datetime.strptime(lineaque[1], '%Y-%m-%d %H:%M:%S')
    if tiempodonde > tiempoque:
        print "el tiempo donde es mayor a tiempo que "
    else:
        indiceDestino+=1
    ultimoSospechoso = Datos()
    UltimoNoSospechoso = Datos(False, lineaque[0], lineaque[1])
    tasaConsumo = -10.0/(120.0*60.0)
    valorActual = fileText[indiceOrigen]
    valorIncorporar = fileTextA[indiceDestino]
    ultimoDato = UltimoNoSospechoso
    cnt = 0
    lista = []
    lista.append(UltimoNoSospechoso)
    while valorIncorporar != valorActual:
        indiceOrigen += 1
        cnt += 1
        valorActual = fileText[indiceOrigen]
        lecturaArchivoDividida = re.split(regexPattern,valorActual)
        if len(lecturaArchivoDividida) < 2:
            break
        if cnt > 1:
            ultimoDato = datoNuevo
        datoNuevo = Datos(False,lecturaArchivoDividida[0],lecturaArchivoDividida[1])
        deltaYmedicion = datoNuevo.altura-ultimoDato.altura
        deltaT = datoNuevo.date-ultimoDato.date
        if deltaT.total_seconds() < 1:
            deltaT = datetime.timedelta(seconds=1)
        deltaYvalido = datoNuevo.altura - UltimoNoSospechoso.altura
        deltaTvalido = datoNuevo.date - UltimoNoSospechoso.date
        if deltaTvalido.total_seconds() < 1:
            deltaTvalido = datetime.timedelta(seconds=1)
        esperado = UltimoNoSospechoso.altura - tasaConsumo*(datoNuevo.date-UltimoNoSospechoso.date).total_seconds()
        if esperado < 28.:
            esperado = 90.
        if cnt > 1:
            if deltaYvalido/deltaTvalido.total_seconds() < 1.5*tasaConsumo: #Regla consumo   
                datoNuevo.descartar = True
            if deltaYvalido > 2. and (UltimoNoSospechoso.altura > 45. or deltaT.total_seconds() < 6*60 or datoNuevo.altura < 80. or deltaTvalido.total_seconds < 20*60): #Regla Falso repostaje
                datoNuevo.descartar = True
            if abs(datoNuevo.altura - esperado) < .3: #Regla esperanza
                datoNuevo.descartar = False
            if UltimoNoSospechoso.altura < 35. and esperado > 85. and datoNuevo.altura >= 88:
                datoNuevo.descartar = False      
        if datoNuevo.descartar:
            ultimoSospechoso = datoNuevo
        else:
            UltimoNoSospechoso = datoNuevo
            lista.append(datoNuevo)
    print cnt        
    while len(lista) > 0:
        dato = lista.pop(-1)
        fileTextA.insert(indiceDestino, str(datoNuevo.altura)+","+datoNuevo.date.strftime('%Y-%m-%d %H:%M:%S'))    
        x.insert(indiceDestino, dato.date)
        y.insert(indiceDestino, dato.altura)

def truncate(number, digits):
    stepper = 10.0 * digits
    return math.trunc(stepper * float(number)) / stepper

def onclick(event):
    global control_down
    global alt_down
    if control_down: #agregar data
        print "Agregar"
        que = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileText) - 1, fileText)       
        donde = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileTextA) - 1, fileTextA)
        print que, donde, fileText[que], fileTextA[donde]
        arreglarDatosaTramosEinsertar(que,donde)
        xlims = ax1.get_xlim() # se obtiene el valor de la cordenada xlim
        ylims = ax1.get_ylim() # se obtiene el valor de la cordenada ylim 
        ax1.clear() # se limpia 
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')
        plt.grid(True)
        ax1.set_xlim(xlims) # seteo el ultimo valor de la coordenada xlim 
        ax1.set_ylim(ylims) # seteo el ultimo valor de la coordenada ylim 
        fig.canvas.draw()
        plt.show()
    if alt_down: #eliminar data
        print "Eliminar"
        resultado = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileTextA) - 1, fileTextA)       
        x.pop(resultado)
        y.pop(resultado)
        fileTextA.pop(resultado)
        xlims = ax1.get_xlim()  # se obtiene el valor de la cordenada xlim antes del clear
        ylims = ax1.get_ylim() # se obtiene el valor de la cordenada ylim antes del clear 
        ax1.clear()
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')
        plt.grid(True)
        ax1.set_xlim(xlims) # seteo el ultimo valor de la coordenada xlim despues del clear
        ax1.set_ylim(ylims) # seteo el ultimo valor de la coordenada ylim despues del clear
        fig.canvas.draw()
        plt.show()
         
def on_key_press(event):
    global control_down
    global alt_down
    if event.key == 'control':
        control_down = True
    if event.key == 'alt':
        alt_down = True

def on_key_release(event):
    global control_down
    global alt_down
    global alt_s #guardar
    if event.key == 'control':
        control_down = False
    if event.key == 'alt':
        alt_down = False
    if event.key == 'alt+s':
        fpArregladosFinal = "CDH"+caexNumber+"CAEX.csv"
        with open(fpArregladosFinal, "w") as ff:# creo un archivo 
            for row in range(len(fileTextA)-1):
                linea = str(y[row])+","+x[row].strftime('%Y-%m-%d %H:%M:%S')
                print >> ff, linea
            ff.close()

def buscarValorCercano(dateBuscar, alturaBuscar, L, R, lista):
    m = int((L+R)/2)
    linea = re.split(regexPattern, lista[m])
    elegido = -1
    try:
        dt = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S.%f')
    except:
        dt = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S')

    if L > R:
        print "retorno vacio"
        return 0 

    if R - L <= 10:
        if R - L == 0:
            print "Solo uno"
            return L
        else:
            menorDelta = 100000.0
            retorno = L    
            for i in range(L,R):    
                linea = re.split(regexPattern, lista[i])
                try:
                    dt1 = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S.%f')
                except:
                    dt1 = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S')
                datetimeDeltaL = dateBuscar.replace(tzinfo=None) - dt1.replace(tzinfo=None)
                if abs(datetimeDeltaL.total_seconds()) < menorDelta:
                    menorDelta = abs(datetimeDeltaL.total_seconds())
                    retorno = i
            return retorno        
        return masCercano   

    if dt.replace(tzinfo=None) > dateBuscar.replace(tzinfo=None):
        elegido = buscarValorCercano(dateBuscar, alturaBuscar, L, m-1, lista)
    if dt.replace(tzinfo=None) < dateBuscar.replace(tzinfo=None):
        elegido = buscarValorCercano(dateBuscar, alturaBuscar, m+1, R, lista)           

    return elegido
caexNumber = sys.argv[1]

if len(sys.argv) > 2:
    fpOriginales = "CDH"+caexNumber+"RAW Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+"RAW Arreglados.csv"
else:    
    fpOriginales = "CDH"+caexNumber+" Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+" Arreglados.csv"

lineCounter = 0

with open(fpArreglados) as fp:
    fileTextA = fp.read()
    fileTextA = re.split('|'.join(map(re.escape, "\n")), fileTextA)
    delimiters = "'",",","\n"
    regexPattern = '|'.join(map(re.escape, delimiters))
    x = []
    y = []
    for line in fileTextA:
        lineCounter += 1
        datosNuevos = re.split(regexPattern, line)
        if len(datosNuevos) < 2:
            break
        try:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S.%f')
        except:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S')
        x.append(dtMeasure)
        y.append(truncate(datosNuevos[0],1))
    lineCounter = 0
    with open(fpOriginales) as f:
        fileText = f.read()
        fileText = re.split('|'.join(map(re.escape, "\n")), fileText)
        delimiters = "'",",","\n"
        regexPattern = '|'.join(map(re.escape, delimiters))
        x2 = []
        y2 = []
        for line in fileText:
            lineCounter += 1
            datosNuevos = re.split(regexPattern, line)
            if len(datosNuevos) < 2:
                break
            try:
                dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S.%f')
            except:
                dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S')
            x2.append(dtMeasure)
            y2.append(truncate(datosNuevos[0],1))
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        cidMouse = fig.canvas.mpl_connect('button_press_event', onclick)
        cidKeyPress = fig.canvas.mpl_connect('key_press_event', on_key_press)
        cidKeyRelease = fig.canvas.mpl_connect('key_release_event', on_key_release)
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        theplot = ax1.plot(x, y, c='r', marker="o", label='Arreglados')[0]
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()