import sys
import Queue
import time, datetime
import re
import os

class Datos:
    def __init__(self, descartar=False, altura=0.0, date="2018-01-1 00:00:00.0"):
        self.descartar = descartar
        self.altura = float(altura)
        deli = ".","\n"
        fecha = re.split('|'.join(map(re.escape, deli)),date)
        try:
            self.date = datetime.datetime.strptime(fecha[0], '%Y-%m-%d %H:%M:%S.%f')
        except:
            self.date = datetime.datetime.strptime(fecha[0], '%Y-%m-%d %H:%M:%S')

listaSize = 150
lista = []
caexNumber = sys.argv[1]
if len(sys.argv) > 2:
    fpOriginales = "CDH"+caexNumber+"RAW Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+"RAW Arreglados.csv"
else:    
    fpOriginales = "CDH"+caexNumber+" Ordenado.csv"
    fpArreglados = "CDH"+caexNumber+" Arreglados.csv"

with open(fpOriginales) as fp:
   with open(fpArreglados, "w") as fw:
    line = fp.readline()
    cnt = 0
    delimiters = "'",","
    regexPattern = '|'.join(map(re.escape, delimiters))
    lecturaArchivoDividida = re.split(regexPattern,line)
    datoNuevo = Datos(False,lecturaArchivoDividida[0],lecturaArchivoDividida[1])
    esperado = lecturaArchivoDividida[0]
    lista.append(datoNuevo)
    ultimoSospechoso = Datos()
    UltimoNoSospechoso = datoNuevo
    tasaConsumo = -10.0/(120.0*60.0)
    while line:
        line = fp.readline()
        cnt += 1
        lecturaArchivoDividida = re.split(regexPattern,line)
        if len(lecturaArchivoDividida) < 2:
            break
        datoNuevo = Datos(False,lecturaArchivoDividida[0],lecturaArchivoDividida[1])
        deltaYmedicion = datoNuevo.altura-lista[len(lista)-1].altura
        deltaT = datoNuevo.date-lista[len(lista)-1].date
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


        lista.append(datoNuevo)

        if datoNuevo.descartar:
            ultimoSospechoso = datoNuevo
        else:
            UltimoNoSospechoso = datoNuevo
                
        if len(lista)> listaSize:
            datoNuevo = lista.pop(0)
            if not datoNuevo.descartar:
                linea = str(datoNuevo.altura)+","+datoNuevo.date.strftime('%Y-%m-%d %H:%M:%S')
                print >> fw, linea
    fw.close()
fp.close()

#if len(sys.argv) < 2:
#    os.system("Plot.py "+caexNumber)
#else:
#    os.system("Plot.py "+caexNumber+" 1")