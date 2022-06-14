import time
import subprocess
from threading import Timer

###################################################################################
################################# USER INPUTS #####################################
###################################################################################

#Number of Attempts Allowed 
NumberofAtt=int(raw_input("Please enter the number of attempts allowed before blocking: "))

#Blocking Time
BlockingTime=int(raw_input("How long do you want to block the IP for? Enter in seconds: "))

#Target log file
targetfile=raw_input("Please enter the log file directory: ")

###################################################################################
################################ SCRIPT ###########################################
###################################################################################

#Tracks the log file, equivalent of tail -F
def follow(thefile):
	thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

#Split each line to a list, getting the IP address from the list
def getip(line):
	elementslist= []
	elements = line.split()
	for element in elements:
		elementslist.append(element)
	#print elementslist
	return elementslist[10]
	#print elementslist[10]


#Track the log
#f = open("/var/log/secure")
f = open(str(targetfile))
lines = follow(f)

#Create dictionary for counting each IP
ipcount = {}


#Counts each attempt by the IP
for i in lines:
	if (i.find('Failed password')!=-1):
		print i
		ipaddr=getip(i)
		if ipaddr in ipcount:
			ipcount[ipaddr]+= 1
		else:
			ipcount[ipaddr] = 1
		print "This IP has reached "+str(ipcount[ipaddr])+" Attempts"
		
		#If attempts exceeds the amount entered at the start, drop the IP for the specified amount of time
		if ipcount[ipaddr] >= NumberofAtt:
			print "More than "+str(NumberofAtt)+" attempts, IP is blocked"
			ipcount[ipaddr] = 0;
			subprocess.call('iptables -A INPUT -s '+ipaddr+' -j DROP',shell=True)
			def release_ip():
				subprocess.call('iptables -D INPUT -s '+ipaddr+' -j DROP',shell=True)

			t= Timer(BlockingTime,release_ip)
			t.start()
	#Clear the counter if user correctly enters the password
	elif (i.find('Accepted password') !=-1):
		ipaddr=getip(i)
		ipcount[ipaddr] = 0
	else:
		continue
	