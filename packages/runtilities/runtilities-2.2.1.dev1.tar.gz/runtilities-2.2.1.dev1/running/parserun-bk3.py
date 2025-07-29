#!/usr/bin/python
# ##########################################################################################
#	parserun.py
#		parse run from garmin training center
#
#	Date		Author		Reason
#	----		------		------
#	10/25/09	Lou King	Create
#
# ##########################################################################################

# standard
import optparse
import datetime
import re
import os
import math

# home grown
from running.running import xmldict

MHR = 204				# Lou's MHR.  Change for yours
METERPMILE = 1609.3439941
EPSILON = METERPMILE - 1600 + 1	# make sure 1600 ~= mile

# ##########################################################################################
def timestr(
	tsm):
#		return time in seconds per mile
# ##########################################################################################
	
	# parse out the integer and microsecond portion.  Add 1/2 second for rounding
	tsec = int(tsm)
	tusec = ((tsm-tsec)*1E6)+.5E6
	
	# add the duration in seconds, microseconds to epoch time of 0, allowing reformat using strftime function
	d = datetime.timedelta (0, tsec, tusec)
	dt1 = datetime.datetime(2009,1,1,0,0,0)
	dt2 = dt1 + d
	
	# if it's greater than an hour, then show the hours, else just show minutes:seconds
	if (tsec+(tusec/1E6) > 60*60):
		fmt = "%H:%M:%S" 
	else:
		fmt = "%M:%S"
	s = dt2.strftime(fmt)
	
	# get rid of leading 0, if present
	s = re.sub('^0','',s)
	
	return s;

# ##########################################################################################
def pace (
#		return pace in seconds per mile
	ts, 
#		time in seconds
	d):
#		distance in meters
# ##########################################################################################

	# calculate time in seconds per mile
	tsm = ts * (METERPMILE / d)
	
	return timestr(tsm)

# ##########################################################################################
#	__main__
# ##########################################################################################

usage = "usage: %prog [options] <tcxfile> <laplist>\n\n"
usage += "where:\n"
usage += "  <tcxfile>\tfile output from Garmin Training Center\n"
usage += "  <laplist> is one of two formats:\n"
usage += "     no switches\tsets of laps to be averaged, i.e., 5,3 means average first 5 laps, next 3 laps, then remaining\n"
usage += "     -interval\tnum laps before first workout then num repeats\n"

parser = optparse.OptionParser(usage=usage)
parser.add_option("-i", "--interval", dest="interval", action="store_true", help="treat input as intervals: num laps before first workout then num repeats")
parser.set_defaults(interval=False)
(options, args) = parser.parse_args()

tcxfile = args.pop(0)
laplist = args.pop(0)
sets = [int(si) for si in laplist.split(',')]
numsets = len(sets)

root = xmldict.readXmlFile(tcxfile)
laps = root['TrainingCenterDatabase']['Activities']['Activity']['Lap']

numlaps = len(laps)

# set up uselap (ul) array
ul = [True for i in range(numlaps)]

# if interval (-interval) switch is set, reset to use a single set, and update uselap (ul) array
# to force accumulation of only the indicated repeats
if (options.interval):
	ul = [False for i in range(numlaps)]
	(numbefore,numint) = sets
	for i in range(numint):
		ul[numbefore+i*2] = True

	sets = [numlaps,]
	numsets = 0


more = True
l = 0
tttime = 0
tthrtime = 0
tthr = 0
ttdist = 0

setstr = ""
csvstr = "distance,time,pace,avghr\n"
pacesstr = {}
for s in range(numsets+1):  # and more
	ttime = 0
	thrtime = 0
	thr = 0
	tdist = 0
	if s < numsets:
		setlimit = sets[s]
	else:
		setlimit = numlaps # numlaps for conventient ceiling for limit
	for i in range(setlimit): 	# and more; i++) {
		time = float(laps[l]['TotalTimeSeconds'])
		hr   = int(laps[l]['AverageHeartRateBpm']['Value'])
		dist = float(laps[l]['DistanceMeters'])		# bug in xmldict?  Seems to put into a list if any child tag has the same name
		
		if dist != 0.0:
		
			# accumulate for this set
			# for interval switch, only indicated laps are averaged
			if (ul[l]):
				ttime += time
				if (l!=0):
					thrtime += time 
					thr += hr * time
				
				tdist += dist
			
			
			# accumulate for whole run
			tttime += time
			if (l!=0):
				tthrtime += time
				tthr += hr * time
			
			ttdist += dist
			
			pacesstr[l] = pacesstr.setdefault(l,"") + timestr(time) + "({0:d})".format(hr)
			csvstr += "{0:.2f},{1},{2},{3}\n".format(dist/METERPMILE,timestr(time),pace(time,dist),hr)

			# indicate distance=pace for odd-distanced splits
			if (dist != METERPMILE):
				pacesstr[l] += " [{0:.2f}={1}]".format(dist/METERPMILE,pace(time,dist))

		# weird 0 distance lap
		else:
			pacesstr[l] = pacesstr.setdefault(l,"") + timestr(time) + "({0:d})".format(hr)
			
		l += 1
		if (l == numlaps):
			more = False
			break
	
	# calculate averages over this set
	if thrtime > 0:
		ahr = int ((thr / thrtime) + 0.5)
	else:
		ahr = "n/a"
	apace = pace (ttime, tdist)
	adist = tdist / METERPMILE
	if s < numsets:
		intmiles = int(adist+0.5)
		if math.fabs(tdist/intmiles-METERPMILE) < EPSILON:
			adistpr = int(adist+EPSILON/METERPMILE)
		else:
			adistpr = adist 
	else: 
		adistpr = "{0:.2f}".format(adist)
	
	if (s > 0):
		setstr += ", "
	setstr += "{0}@{1}({2})".format(adistpr,apace,ahr)

	if not more:
		break
	

# calculate averages over the whole run
athr = int ((tthr / tthrtime) + 0.5)
atpace = pace (tttime, ttdist)
atdist = ttdist / METERPMILE
totstr = "{0:.1f} miles, {1}, {2}/mi, AHR {3} ({4}% MHR)".format (atdist, timestr(tttime), atpace, athr, int((athr*100/MHR)+0.5))

CSV = open ("history.csv","w")
CSV.write (csvstr)
CSV.close()

OUT = open ("temp.txt","w")
OUT.write ("{0}\n".format(totstr))
OUT.write ("{0}\n\n".format(setstr))
if (options.interval):
	OUT.write ("splits:\n")
	for l in range(numlaps):
		if (ul[l]):
			OUT.write ("{0}\n".format(pacesstr[l]))
	OUT.write ("\n")

OUT.write ("all splits:\n")
for l in range(numlaps):
	split = l+1
	OUT.write ("{0} - {1}\n".format(split,pacesstr[l]))

OUT.close()
os.startfile ("temp.txt")
