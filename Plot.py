import matplotlib.pyplot as plt
import datetime
import re
import math
import sys

def truncate(number, digits):
    stepper = 10.0 * digits
    return math.trunc(stepper * float(number)) / stepper

caexNumber = sys.argv[1]

if len(sys.argv) == 2:
    fpOriginales = "CDH"+caexNumber+"RAW Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+"CAEX.csv"
    #fpArreglados = "CDH"+caexNumber+"RAW Arreglados.csv"
else: 
    fpOriginales = "CDH"+caexNumber+"RAW Arreglados.csv"
    fpArreglados = "CDH"+caexNumber+"CAEX.csv"


with open(fpArreglados) as fp:
    line = fp.readline()
    delimiters = "'",",","\n"
    regexPattern = '|'.join(map(re.escape, delimiters))
    datosNuevos = re.split(regexPattern,line)
    x = []
    y = []
    try:
        dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S.%f')
    except:
        dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S')
    x.append(dtMeasure)
    y.append(truncate(datosNuevos[0],1))
    while line: 
        line = fp.readline()
        datosNuevos = re.split(regexPattern,line)
        if len(datosNuevos) < 2:
            break
        try:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S.%f')
        except:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S')
        x.append(dtMeasure)
        y.append(truncate(datosNuevos[0],1))
        
    with open(fpOriginales) as f:
        line = f.readline()
        datosNuevos = re.split(regexPattern,line)
        x2 = []
        y2 = []
        try:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S.%f')
        except:
            dtMeasure = datetime.datetime.strptime(datosNuevos[1], '%Y-%m-%d %H:%M:%S')
        x2.append(dtMeasure)
        y2.append(truncate(datosNuevos[0],1))
        while line: 
            line = f.readline()
            datosNuevos = re.split(regexPattern,line)
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
        ax1.plot(x2, y2, c='b', marker="x", label='Originales')
        ax1.plot(x, y, c='r', marker="o", label='Arreglados')
        plt.legend(loc='upper left');
        plt.grid(True)
        plt.show()