import sys
import csv
import time, datetime
import re
import RepararDataAMano1


numCAEX = sys.argv[1]

delimiters = "."
regexPattern = '|'.join(map(re.escape, delimiters))

caexNumber = sys.argv[1]
if len(sys.argv) > 2:
    origen = "CDH"+caexNumber+"RAW.csv"
    destino = "CDH"+caexNumber+"RAW Ordenado.csv"
else:    
    origen = "CDH"+caexNumber+".csv"
    destino = "CDH"+caexNumber+" Ordenado.csv"

reader = csv.reader(open(origen), delimiter=",", quoting=csv.QUOTE_MINIMAL)
sortedlist = sorted(reader, key=lambda row: row[1], reverse=False)

with open(destino, "w") as fp:
    for row in sortedlist:
    	linea2 = re.split(regexPattern, row[1])
        linea = row[0]+","+linea2[0]
        
        print >> fp, linea
        #print >> fp, row
        
fp.close()