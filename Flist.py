#! /usr/bin/env python

###################################################################
##								 ##
## Name: TBrate.py						 ##
## Author: Kevin Nash 						 ##
## Date: 5/28/2015						 ##
## Purpose: This program creates the numerator and denominator 	 ##
##          used by TBTrigger_Maker.py to create trigger  	 ##
##          Efficiency curves.					 ##
##								 ##
###################################################################

import os
import sys
from DataFormats.FWLite import Events, Handle
from optparse import OptionParser
from array import *

import Bstar_Functions	
from Bstar_Functions import Load_Ntuples



saveout = sys.stdout
#Based on what set we want to analyze, we find all Ntuple root files 
arr = ['QCDHT500','QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000','data','ttbar','singletop_s','singletop_t','singletop_tB']

for jj in range(12,31):
	if jj%2!=0:
		continue 
	arr.append('signalRH'+str(jj*100))
	arr.append('signalLH'+str(jj*100))


for i in arr:
	Outf1   =   open("Files_"+i+".txt", "w")
	files = Load_Ntuples(i)
	sys.stdout = Outf1
	for file1 in files:
		if file1.find("root")!=-1:
			print file1
	sys.stdout = saveout

