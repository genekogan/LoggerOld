import csv

def get_openpaths_gps():
	gpsdata = csv.reader(open('openpaths_genekogan.csv', 'rb'), dialect='excel', delimiter=',')
	gpsdata.next()
	gps = []
	for row in gpsdata:
		lat = float(row[0])
		lng = float(row[1])
		date = row[3]
		source = row[4]
		if source=="samsung SGH-I777":
			gps.append([date,lat,lng])
		#print source + " : " + date + " : (" + lat + ", " + lng + ")"
	return gps
	
print get_openpaths_gps()