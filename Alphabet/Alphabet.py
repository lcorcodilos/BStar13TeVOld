# Class def for full Alphabetization.
# Does everything except the pretty plots, but makes all components available.

import os
import math
from array import array
import optparse
import ROOT
from ROOT import *
import scipy

# Our functions:
import Alphabet_Header
from Alphabet_Header import *
import Plotting_Header
from Plotting_Header import *
import Converters
from Converters import *
import Distribution_Header
from Distribution_Header import *

class Alphabetizer:
	def __init__(self, name, Dist_Plus, Dist_Minus):
		self.name = name
		self.DP = Dist_Plus
		self.DM = Dist_Minus
	def SetRegions(self, var_array, presel):
	# var_array = [x var, y var, x n bins, x min, x max, y n bins, y min, y max]
		self.X = var_array[0]
		self.Pplots = TH2F("added"+self.name, "", var_array[2], var_array[3],var_array[4],var_array[5],var_array[6],var_array[7])
		self.Mplots = TH2F("subbed"+self.name, "", var_array[2], var_array[3],var_array[4],var_array[5],var_array[6],var_array[7])
		for i in self.DP:
			quick2dplot(i.File, i.Tree, self.Pplots, var_array[0], var_array[1], presel, i.weight)
		for j in self.DM:
			quick2dplot(j.File, j.Tree, self.Mplots, var_array[0], var_array[1], presel, j.weight)
		self.TwoDPlot = self.Pplots.Clone("ThreeDPlot_"+self.name)
		self.TwoDPlot.Add(self.Mplots, -1.)
	# def GetRates(self, cut, bins, truthbins, center, FIT):
	# 	self.center = center
	# 	self.G = AlphabetSlicer(self.TwoDPlot, bins, cut[0], cut[1], center) # makes the A/B slices
	# 	if len(truthbins)>0:
	# 		self.truthG = AlphabetSlicer(self.TwoDPlot, truthbins, cut[0], cut[1], center) # makes the A/B slices
	# 	else:
	# 		self.truthG = None
	# 	self.Fit = FIT # reads the right class in, should be initialized and set up already
	# 	AlphabetFitter(self.G, self.Fit) # creates all three distributions (nominal, up, down)
	# def Get3DRates(self, cut1, cut2, bins, truthbins, center, FIT):
	# 	self.center = center
	# 	self.G = Alphabet3DSlicer(self.ThreeDPlot, bins, cut1[0], cut1[1], cut2[0], cut2[1], center) # makes the A/B/C slices
	# 	if len(truthbins)>0:
	# 		self.truthG = Alphabet3DSlicer(self.ThreeDPlot, truthbins, cut1[0], cut1[1], cut2[0], cut2[1], center) # makes the A/B/C slices
	# 	else:
	# 		self.truthG = None
	# 	self.Fit = FIT # reads the right class in, should be initialized and set up already
	# 	AlphabetFitter(self.G, self.Fit) # creates all three distributions (nominal, up, down)
	def doRates(self, var, varCuts, passCuts, presel, bins, truthbins, fitFunc):
		# LC 11/1/17
		# Does the job of SetRegions and GetRates but doesn't waste time making a multi-dimensional histogram
		# to define cut regions (which is an inexact method!)
		# var - tree variable that we want to look at in range we want to see it
		# varCuts - ex '(mass_top<105)||(mass_top>210)'
		# passCuts - cuts to define 'pass'; a string like '(sjbtag>0.5426)&&(tau32<0.65)'
		# presel - preselection that's always applied
		# bins - bins for var
		self.G = AlphabetNDSlicer(self.DP, self.DM, var, varCuts, passCuts, presel, bins)
		if len(truthbins)>0:
			self.truthG = AlphabetNDSlicer(self.DP, self.DM, var, '!('+varCuts+')', passCuts, presel, truthbins) # makes the A/B/C slices
		else:
			self.truthG = None

		self.Fit = fitFunc # reads the right class in, should be initialized and set up already
		AlphabetFitter(self.G, self.Fit) # creates all three distributions (nominal, up, down)

	def doRatesFlexFit(self, var, varCuts, passCuts, presel, bins, truthbins, fitFunc, center=0):
		# LC 11/14/17
		# Same as doRates but with more flexible fit

		self.G = AlphabetNDSlicer(self.DP, self.DM, var, varCuts, passCuts, presel, bins, center)
		if len(truthbins)>0:
			self.truthG = AlphabetNDSlicer(self.DP, self.DM, var, '!('+varCuts+')', passCuts, presel, truthbins, center) # makes the A/B/C slices
		else:
			self.truthG = None

		# Now do the fitting
		self.fitFunc = fitFunc
		print str(bins[0]-center) + ', ' + str(bins[-1]-center)
		self.Fit = TF1("fit", self.fitFunc, bins[0]-center, bins[-1]-center)
		self.FitResults = self.G.Fit(self.Fit)

		self.G.Draw()
		raw_input('waiting')


		self.EG = TGraphErrors(1000)
		for i in range(1000):
			self.EG.SetPoint(i, bins[0]-center + i*(bins[-1]- bins[0])/1000., 0)
		TVirtualFitter.GetFitter().GetConfidenceIntervals(self.EG)
		self.EG.SetLineColorAlpha(kRed,0.2)
		self.Ndof = self.Fit.GetNDF()
		self.Chi2 = self.Fit.GetChisquare()

	


	# DOESN'T WORK WITH CURRENT FITTING CODE
	def MakeEst(self, var_array, rate_var, antitag, tag, center=0):
	# makes an estimate in a region, based on an anti-tag region, of that variable in all dists
	# var_array - array for what we are plotting 
	# rate_var - var in which the rate was made
		self.Fit.MakeConvFactor(rate_var, center)
		self.hists_EST = []
		self.hists_EST_SUB = []
		self.hists_EST_UP = []
		self.hists_EST_SUB_UP = []
		self.hists_EST_DN = []
		self.hists_EST_SUB_DN = []
		self.hists_MSR = []
		self.hists_MSR_SUB = []
		self.hists_ATAG = []
		for i in self.DP:
			temphist = TH1F("Hist_VAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistN = TH1F("Hist_NOMINAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistU = TH1F("Hist_UP"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistD = TH1F("Hist_DOWN"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistA = TH1F("Hist_ATAG"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			quickplot(i.File, i.Tree, temphist, var_array[0], tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFact+")")
			quickplot(i.File, i.Tree, temphistU, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFactUp+")")
			quickplot(i.File, i.Tree, temphistD, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFactDn+")")
			quickplot(i.File, i.Tree, temphistA, var_array[0], antitag, i.weight)
			self.hists_MSR.append(temphist)
			self.hists_EST.append(temphistN)
			self.hists_EST_UP.append(temphistU)
			self.hists_EST_DN.append(temphistD)
			self.hists_ATAG.append(temphistA) 
		for i in self.DM:
			temphist = TH1F("Hist_SUB_VAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistN = TH1F("Hist_SUB_NOMINAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistU = TH1F("Hist_SUB_UP"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistD = TH1F("Hist_SUB_DOWN"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistA = TH1F("Hist_SUB_ATAG"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			quickplot(i.File, i.Tree, temphist, var_array[0], tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFact+")")
			quickplot(i.File, i.Tree, temphistU, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFactUp+")")
			quickplot(i.File, i.Tree, temphistD, var_array[0], antitag, "("+i.weight+"*"+self.Fit.ConvFactDn+")")
			quickplot(i.File, i.Tree, temphistA, var_array[0], antitag, i.weight)
			self.hists_MSR_SUB.append(temphist)
			self.hists_EST_SUB.append(temphistN)
			self.hists_EST_SUB_UP.append(temphistU)
			self.hists_EST_SUB_DN.append(temphistD)
			self.hists_ATAG.append(temphistA)

	def MakeEstFlexFit(self, var_array, rate_var, antitag, tag, center=0):
	# makes an estimate in a region, based on an anti-tag region, of that variable in all dists
	# var_array - array for what we are plotting 
	# rate_var - var in which the rate was made
		print self.fitFunc
		fitString = CustomFit2String(rate_var,self.Fit,self.fitFunc,str(center))
		print 'Fit = ' + fitString
		self.hists_EST = []
		self.hists_EST_SUB = []
		self.hists_MSR = []
		self.hists_MSR_SUB = []
		self.hists_ATAG = []
		for i in self.DP:
			temphist = TH1F("Hist_VAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistN = TH1F("Hist_NOMINAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistA = TH1F("Hist_ATAG"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			quickplot(i.File, i.Tree, temphist, var_array[0], tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, var_array[0], antitag, "("+i.weight+"*"+fitString+")")
			quickplot(i.File, i.Tree, temphistA, var_array[0], antitag, i.weight)
			self.hists_MSR.append(temphist)
			self.hists_EST.append(temphistN)
			self.hists_ATAG.append(temphistA) 
		for i in self.DM:
			temphist = TH1F("Hist_SUB_VAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistN = TH1F("Hist_SUB_NOMINAL"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			temphistA = TH1F("Hist_SUB_ATAG"+self.name+"_"+i.name, "", var_array[1], var_array[2], var_array[3])
			quickplot(i.File, i.Tree, temphist, var_array[0], tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, var_array[0], antitag, "("+i.weight+"*"+fitString+")")
			quickplot(i.File, i.Tree, temphistA, var_array[0], antitag, i.weight)
			self.hists_MSR_SUB.append(temphist)
			self.hists_EST_SUB.append(temphistN)
			self.hists_ATAG.append(temphistA)

	def MakeEstVariable(self, variable, binBoundaries, antitag, tag):
		# makes an estimate in a region, based on an anti-tag region, of that variable in all dists
		# self.Fit.MakeConvFactor(self.X, self.center)
		self.hists_EST = []
		self.hists_EST_SUB = []
		self.hists_EST_UP = []
		self.hists_EST_SUB_UP = []
		self.hists_EST_DN = []
		self.hists_EST_SUB_DN = []
		self.hists_MSR = []
		self.hists_MSR_SUB = []
		self.hists_ATAG = []
		for i in self.DP:
			temphist = TH1F("Hist_VAL"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistN = TH1F("Hist_NOMINAL"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistU = TH1F("Hist_UP"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistD = TH1F("Hist_DOWN"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistA = TH1F("Hist_ATAG"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			quickplot(i.File, i.Tree, temphist, variable, tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFact+")")
			quickplot(i.File, i.Tree, temphistU, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFactUp+")")
			quickplot(i.File, i.Tree, temphistD, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFactDn+")")
			quickplot(i.File, i.Tree, temphistA, variable, antitag, i.weight)
			self.hists_MSR.append(temphist)
			self.hists_EST.append(temphistN)
			self.hists_EST_UP.append(temphistU)
			self.hists_EST_DN.append(temphistD)
			self.hists_ATAG.append(temphistA)
		for i in self.DM:
			temphist = TH1F("Hist_SUB_VAL"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistN = TH1F("Hist_SUB_NOMINAL"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			temphistU = TH1F("Hist_SUB_UP"+self.name+"_"+i.name, "",len(binBoundaries)-1, array('d',binBoundaries))
			temphistD = TH1F("Hist_SUB_DOWN"+self.name+"_"+i.name, "", len(binBoundaries)-1, array('d',binBoundaries))
			quickplot(i.File, i.Tree, temphist, variable, tag, i.weight)
			quickplot(i.File, i.Tree, temphistN, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFact+")")
			quickplot(i.File, i.Tree, temphistU, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFactUp+")")
			quickplot(i.File, i.Tree, temphistD, variable, antitag, "("+i.weight+"*"+self.Fit.ConvFactDn+")")
			self.hists_MSR_SUB.append(temphist)
			self.hists_EST_SUB.append(temphistN)
			self.hists_EST_SUB_UP.append(temphistU)
			self.hists_EST_SUB_DN.append(temphistD)
	
def CustomFit2String(var,fit,fitFunc,center):
	# Need to convert the fitFunc (of form '[0]+[1]*x...') to a string
	# with the actual parameters in for [0],[1], etc and 'x' replace with our var
	thisFitFunc = '('
	
	# Need to have our own find algo to avoid messing up exp when 'x' gets replaced with var
	# .find cannot be used with .replace because .find only finds the index of the first instance and
	# .replace replaces all instances. Can't pick and choose instances then.

	# Build an index of all 'real x's
	xIndex = []
	for ichar in range(len(fitFunc)):
		char = fitFunc[ichar]
		if char == "x" and fitFunc[ichar-1] != 'e' and fitFunc[ichar+1] != 'p':
			xIndex.append(ichar)

	# Now build a new string with any 'real' x replaced by var
	for ix in range(len(xIndex)):
		# If on the first value, start at 0, end at first x
		if ix == 0:
			start = 0
			stop = xIndex[ix]
		# otherwise, start IN FRONT of the ix-1 value (+1 because you don't want to include the x)
		else:
			start = xIndex[ix-1]+1
			stop = xIndex[ix]
		# need to grab left side of string and then rebuild the string
		leftside = fitFunc[start:stop]

		thisFitFunc += leftside + '(' + var + '-' + str(center) + ')'
		print thisFitFunc
	# Finish up by adding the final right side
	thisFitFunc += fitFunc[xIndex[-1]+1:]

	# Now swap in the parameter values
	pars = []
	for ipar in range(fit.GetNpar()):
		thisPar = str(fit.GetParameter(ipar))
		thisFitFunc = thisFitFunc.replace('['+str(ipar)+']','('+thisPar+')')

	return thisFitFunc+')'

