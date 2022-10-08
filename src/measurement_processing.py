#!/usr/bin/env python3

def freqmonitoring(config,act_scaled):
    #evaluates the measured frequency values and adds binary states
    #lowerlimit=config.getint('gridcode', 'lowerlimit1')*0.90
    #upperlimit=config.getint('gridcode', 'lowerlimit1')*1.10
    flagFLU1=0
    flagFLL1=0
    if ((act_scaled>=config.getint('gridcode', 'upperlimit1'))==True):
       flagFLU1=1 
    if ((act_scaled<=config.getint('gridcode', 'lowerlimit1'))==True):
       flagFLL1=1        
    flagdict={'flagFLU1':flagFLU1,'flagFLL1':flagFLL1}
    return flagdict