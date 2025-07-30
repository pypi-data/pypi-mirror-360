#!/usr/bin/env python3

import ROOT
import numpy as np
from array import array
import random
import os
import pandas as pd


from fire import Fire

#import prun # looks like mutual import, but it is not really
from  pyfromroot import prun

import ROOT
import time


from  fastnumbers import isfloat




#   the DAT file can contain TAGS:
#   #COLNAME: frame,x,y     ... column names (selfexplaining)
#   #LOAD_AS: x,dx,y,dy     ... order of columns  for x,y,dx,dy TGraph(Errors)
#





#---------------------------------------------
def main( *args , **kwargs):
    """
    kwargs OPTIONS
    opt : same ex0
    color: red blue...
    """
    print("*******DRAW*********")
    print(f"i... @load: args={args}")
    if len(args)==0:
        print("X... no file given")
        return

    fname = args[0]

    ROOT.gDirectory.ls()

    gontainer = ROOT.gDirectory.FindObject( fname )

    print( gontainer )
    print( type(gontainer) )
    import cppyy

    if type(gontainer)==cppyy.gbl.TH1D :
        histo = True
    else:
        histo = False




    canvasname = "draw"
    if "canvas" in kwargs.keys():
        canvasname = kwargs["canvas"]

    drawopt = "" # ...  same ex0  BUT ALSO logy
    drawlogy = False
    if "opt" in kwargs.keys():
        drawopt = "" # kwargs["opt"]
        for dro in kwargs["opt"].split():
            if "same" in dro: drawopt=f"{drawopt} {dro}".strip()
            if "ex0" in dro: drawopt=f"{drawopt} {dro}".strip()
            if "logy" in dro: drawlogy = True


    coloropt = 4 # same ex0
    if "color" in kwargs.keys():
        if kwargs["color"] == "black":     coloropt = 1
        if kwargs["color"] == "red":       coloropt = 2
        if kwargs["color"] == "green":     coloropt = 3
        if kwargs["color"] == "blue":      coloropt = 4
        if kwargs["color"] == "yellow":    coloropt = 5
        if kwargs["color"] == "magenta":   coloropt = 6
        if kwargs["color"] == "cyan":      coloropt = 7
        if kwargs["color"] == "darkgreen": coloropt = 8
        if kwargs["color"] == "gray":      coloropt = 11




    cmain = ROOT.gROOT.GetListOfCanvases().FindObject( canvasname )
    if ROOT.addressof(cmain)==0:
        print(f"i... creating a new /{canvasname}/ canvas")
        #cmain = ROOT.TCanvas(canvasname,canvasname,600,800)
        cmain = ROOT.TCanvas(canvasname,canvasname,600,400)
        print(f"i... creating a new /{canvasname}/ canvas draw")
        cmain.Draw(  ) # CANVAS
        #cmain.Divide(1,2) # div canvas
        #print(f"i... creating a new /{canvasname}/ canvas drawn")
        #cmain = ROOT.gPad.GetCanvas()  # reset all canvas
    else:
        print("--------------existin canvas ------ I cd INTO it",cmain)
        cmain.cd()



    if histo:
        # it will be TH1D
        print("i... ============= OPT=", drawopt)
        gontainer.SetLineColor( coloropt )
        gontainer.SetMarkerColor( coloropt )
        #gontainer.SetLineColor( coloropt )

        print(f"i... DRAWING {gontainer} WITH OPTION ", drawopt )
        gontainer.Draw( drawopt)  # this can be also: same ex0
        if drawlogy:
            ROOT.gPad.SetLogy() #
    else:
        gontainer.SetMarkerStyle(7) # small circle , no lines...
        gontainer.SetMarkerStyle(1) # small circle , no lines...
        gontainer.SetMarkerStyle(22) # small...

        gontainer.Draw("PAW") # no lines...

    # ------------------------------ END OF GRAPH / HISTO : common ----------
    ROOT.gPad.SetGrid()
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    prun.register(cmain, canvasname) # KEY THING TO KEEP CANVAS OVED PRUN MODULE SWITCH

    return





#############################################################################
if __name__=="__main__":
    Fire(main)
    print("H... close canvas to exit...")
    while ROOT.addressof(ROOT.gPad)!=0:
        time.sleep(0.2)
    #input('press ENTER to end...')
