import sys
import Queue
import time, datetime
import re

class Datos:
    def __init__(self, altura=0, date=0):
        self.altura = altura
        self.date = date

#caexNumber = sys.argv[1]
#filepath = "CDH"+caexNumber+".csv";
filepath = "DatosPrueba.csv"

with open(filepath) as fp:
   with open("Datos Prueba Filtrados.csv", "w") as fw:
    x0 = 46.74
    dx = -.15/60
    h = .001
    g = .02
    cnt = 0
    delimiters = "'",","
    regexPattern = '|'.join(map(re.escape, delimiters))
    line = fp.readline()
    datosNuevos = re.split(regexPattern,line)
    last = Datos(datosNuevos[1],datosNuevos[4])
    while True:
        line = fp.readline()
        if not line:
            break
        cnt += 1
        datosNuevos = re.split(regexPattern,line)
        d = Datos(datosNuevos[1],datosNuevos[4])
        try:
            dtMeasure = datetime.datetime.strptime(datosNuevos[4], '%Y-%m-%d %H:%M:%S.%f')
        except:
            dtMeasure = datetime.datetime.strptime(datosNuevos[4], '%Y-%m-%d %H:%M:%S')
        try:    
            dtLast = datetime.datetime.strptime(last.date, '%Y-%m-%d %H:%M:%S.%f')
        except:
            dtLast = datetime.datetime.strptime(last.date, '%Y-%m-%d %H:%M:%S')
        deltaT = dtMeasure - dtLast
        
        xPred = x0 + (dx*deltaT.total_seconds())
        residual = float(datosNuevos[1]) - xPred
        dx = dx + h * (residual / deltaT.total_seconds())
        x0 = xPred + g * residual
        if x0 > 100:
            x0 = 100
        if x0 < 0:
            x0 = 0
                    
        linea = str(x0)+", "+d.date
        print >> fw, linea
        last = Datos(d.altura, d.date)
    
    fw.close()
fp.close()
