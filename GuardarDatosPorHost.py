import time, datetime
import psycopg2
import sys

EPOCH_DATETIME = datetime.datetime(1970,1,1)
SECONDS_PER_DAY = 24*60*60

def utc_to_local_datetime( utc_datetime ):
    delta = utc_datetime - EPOCH_DATETIME
    utc_epoch = SECONDS_PER_DAY * delta.days + delta.seconds
    time_struct = time.localtime( utc_epoch )
    dt_args = time_struct[:6] + (delta.microseconds,)
    return datetime.datetime( *dt_args )
	
if(len(sys.argv) > 1)
    hostName = 'CDH'+sys.argv[1]	
else
	sys.exit("Please add host number as parameter");
	
sql = """
    select ss.double_value_1 as fuel_perc, 
		ss.date as date
    from telemetry.sensor_history ss
	join telemetry.sensor s on ss.sensor_id = s.id
    join operation.equipment e on e.id = s.equipment_id
    where ss.double_value_1 is not null
	and ss.double_value_1 > 0
	and e.name = 'CDH89' 
    and ss.date >= '2019-11-1 00:00:00'::timestamp
    """
conn = psycopg2.connect("host='localhost' dbname='fe' user='postgres' password='postgres'")
cur = conn.cursor()
cur.execute(sql)
rows = cur.fetchall()

with open(hostName+''.csv,'wb') as file:
    print "\nRows:\n"
    for row in rows:
        name = row[0]
        model = row[1]
        fuelPerc = row[2]
        date = row[3]
        line = "{0},{1}\n".format(fuelPerc, utc_to_local_datetime(date))
        print line
        file.write(line)

cur.close()
conn.close()
