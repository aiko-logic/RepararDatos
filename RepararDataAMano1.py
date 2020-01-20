import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import datetime
import re
import math
import sys
import pytz

delimiters = "'",",","\n"
regexPattern = '|'.join(map(re.escape, delimiters))
control_down = False
alt_down = False
lastXlim = 0
lastYlim = 0

global fileTextA


class Datos:
    def __init__(self, descartar=False, altura=0.0, date="2018-01-1 00:00:00"):
        self.descartar = descartar
        self.altura = float(altura)
        deli = ".","\n"
        fecha = re.split('|'.join(map(re.escape, deli)),date)
        self.date = datetime.datetime.strptime(fecha[0], '%Y-%m-%d %H:%M:%S')

def arreglarDatosaTramos(indiceOrigen, indiceDestino):

    ultimoSospechoso = Datos() # dato malo
    data = re.split(regexPattern,fileText[indiceOrigen])
    UltimoNoSospechoso = Datos(False, data[0], data[1]) # dato bueno 
    tasaConsumo = -10.0/(120.0*60.0)
    valorActual = fileText[indiceOrigen] # linea del dato en str
    valorIncorporar = fileTextA[indiceDestino] # linea del dato a incorporar str 
    ultimoDato = UltimoNoSospechoso
    cnt = 0
    lista = []
    while valorIncorporar != valorActual:
        indiceOrigen += 1
        cnt += 1
        valorActual = fileText[indiceOrigen]
        lecturaArchivoDividida = re.split(regexPattern,valorActual)
        if len(lecturaArchivoDividida) < 2:
            break
        if cnt > 1: # en la primera iteracion no entra al if 
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
    #for i in range(0,len(lista)):
    while len(lista) > 0:
        #print "estos son los datos insertados", dato
        dato = lista.pop()

        fileTextA.insert(indiceDestino, str(datoNuevo.altura)+","+datoNuevo.date.strftime('%Y-%m-%d %H:%M:%S'))
        x.insert(indiceDestino, dato.date)
        y.insert(indiceDestino, dato.altura)
         
 



def on_xlims_change(axes):
    #print "updated xlims: ", ax1.get_xlim()
    global lastXlim
    lastXlim = ax1.get_xlim()

def on_ylims_change(axes):
    #print "updated ylims: ", ax1.get_ylim()
    global lastYlim
    lastYlim = ax1.get_ylim()

def truncate(number, digits):
    stepper = 10.0 * digits
    return math.trunc(stepper * float(number)) / stepper



def onclick(event):
    global control_down
    global alt_down
    global lastXlim
    global lastYlim
    if control_down: #agregar data
        print "Agregar"
        que = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileText) - 1, fileText)
        #print 1
        # la linea de "que" busca el valor mas cercano a los datos azules al hacer click      
        donde = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileTextA) - 1, fileTextA)
        #print 2# la linea "donde" es el valor cercano de los datos azules 
        print "el valor que es", que, fileText[que],"el valor donde es", donde, fileTextA[donde]
        lineadonde = re.split(regexPattern, fileTextA[donde])
        #print "esta es la linea donde", lineadonde
        lineaque = re.split(regexPattern, fileText[que])
        #print "esta en la lineaque", lineaque
        #print linea
       
        tiempodonde= datetime.datetime.strptime(lineadonde[1], '%Y-%m-%d %H:%M:%S')#tiempo del dato donde
        print "este es el tiempo donde", tiempodonde
        tiempoque = datetime.datetime.strptime(lineaque[1], '%Y-%m-%d %H:%M:%S')# tiempo del dato que
        print "este es el tiempo que", tiempoque
     
        if tiempodonde > tiempoque:
            print "el tiempo donde es mayor a tiempo que "
        else:
            donde+=1
            print "donde mas 1"
        arreglarDatosaTramos(que, donde)
     
        x.insert(donde, tiempoque)
        y.insert(donde, truncate(lineaque[0],1))
        fileTextA.insert(donde, fileText[que])
        #arreglarDatosaTramos(que, donde)
        ax1.get_position()
        ax1.clear()
        #rreglarDatosaTramos(que, donde)
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')
        plt.grid(True)
        ax1.set_xlim(lastXlim)
        ax1.set_ylim(lastYlim)


        fig.canvas.draw()
        plt.show()

        ax1.set_position()#
        
    if alt_down: #eliminar data
        print "Eliminar"
        resultado = buscarValorCercano(mdate.num2date(event.xdata), event.ydata, 0, len(fileTextA) - 1, fileTextA)       
        #print resultado, fileTextA[resultado]
        #print len(x), len(y), len(fileTextA)
        x.pop(resultado)
        y.pop(resultado)
        fileTextA.pop(resultado)
        #print len(x), len(y), len(fileTextA)
        pos = ax1.get_position()
        ax1.clear()
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')
        plt.grid(True)
        ax1.set_xlim(lastXlim)#
        ax1.set_ylim(lastYlim)
        fig.canvas.draw()
        plt.show()

        ax1.set_position(pos)#

        
def on_key_press(event):
    global control_down # add date 
    global alt_down # delete  date
    global control_s # save the red date 
    if event.key == 'control':
        control_down = True
    if event.key == 'alt':
        alt_down = True
    if event.key == 'alt+s':
        control_s = True

def on_key_release(event):
    global control_down # add date 
    global alt_down # delete date
    global control_s # save the red date
    if event.key == 'control':
        control_down = False
    if event.key == 'alt':
        alt_down = False
    if event.key == 'alt+s':
        alt_s = False
        #fpArreglados = "CDH"+caexNumber+"RAW Arreglados.csv"
        #lineaque = re.split(regexPattern, fileText[que])

        with open(fpArregladosFinal, "w") as ff:# creo un archivo 
            for row in range(len(fileTextA)-1):
                           #f.write(row)
            #linea2 = re.split(regexPattern, row[1])
                linea = str(y[row])+","+x[row].strftime('%Y-%m-%d %H:%M:%S')
    

                print >> ff, linea
                #print "listoo"
        
            ff.close()
        print event.key # funcion para la entrada por teclado 

def buscarValorCercano(dateBuscar, alturaBuscar, L, R, lista):
    m = int((L+R)/2)
    linea = re.split(regexPattern, lista[m])
    elegido = -1
    try:
        dt = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S.%f')
    except:
        dt = datetime.datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S')
    
    #print dt.replace(tzinfo=None), dateBuscar.replace(tzinfo=None), len(lista), L, R, m

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
                print abs(datetimeDeltaL.total_seconds()), dateBuscar, dt1
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
    fpArregladosFinal = "CDH"+caexNumber+"CAEX.csv"
    fpOriginales = "CDH"+caexNumber+"RAW Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+"RAW Arreglados.csv"
else:
    fpArregladosFinal = "CDH"+caexNumber+"CAEX.csv"    
    fpOriginales = "CDH"+caexNumber+" Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+" Arreglados.csv"

lineCounter = 0



with open(fpArreglados) as fp:
    fileTextA = fp.read() # 
    fileTextA = re.split('|'.join(map(re.escape, "\n")), fileTextA)
    #print len(fileTextA)
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

    #print lineCounter
    lineCounter = 0
    with open(fpOriginales) as f:
        fileText = f.read()
        fileText = re.split('|'.join(map(re.escape, "\n")), fileText)
        #print len(fileText)
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
        #print lineCounter
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        cidMouse = fig.canvas.mpl_connect('button_press_event', onclick)
        cidKeyPress = fig.canvas.mpl_connect('key_press_event', on_key_press)
        cidKeyRelease = fig.canvas.mpl_connect('key_release_event', on_key_release)
        ax1.callbacks.connect('xlim_changed', on_xlims_change)
        ax1.callbacks.connect('ylim_changed', on_ylims_change)
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')

        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()