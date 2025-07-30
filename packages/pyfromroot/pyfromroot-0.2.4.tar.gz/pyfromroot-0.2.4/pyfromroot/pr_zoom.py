#!/usr/bin/env python3

import ROOT
import numpy as np
from array import array
import random
import os
import pandas as pd


from fire import Fire
import importlib # dynamic import

import sys # to unload

from pyfromroot import prun   # this seems like mutual import, but it is not really

# ------------------------- MINUIT PART ----------------
#  pip3 install iminout  numba_stats numpy
from iminuit import cost, Minuit
import iminuit
from numba_stats import norm, uniform # faster replacements for scipy.stats functions


import glob





def main( *args ):
    """
    I want to zoom:  object(histo) xlow,xhigh
    """
    display = False # NO DISPLAY HERE
    #display = True #  DISPLAY HERE
    if len(args)<1:
        print("X... no object name given  (and no model given too)")
        return
    if len(args)<2:
        print("X... no zoom limits  given")
        return


    fname = args[0]
    g_orig = ROOT.gDirectory.FindObject(f"{fname}")


    # - check the object. If None => try to load something
    #        AUTOMATIC LOAD => special, will be removed in future
    #
    if g_orig==None:
        print(f"X... {fname} object doesnot exist in gDirectory")
        # - do we try to load it? If it is an actual file
        if os.path.exists(fname):
            print(f"i... BUT file /{fname} exists")
            print(f" ...       trying to unload and load /pr_load/")
            try:
                sys.modules.pop( "pr_load" )
            except:
                pass
            module_load = importlib.import_module( "pr_load" )
            ok = False
            try:
                if len(args)>1: # accept y,x as 2nd parameter
                    module_load.main( fname , args[2] )
                else:
                    module_load.main( fname  )
                ok = True
            except:
                ok = False
            if not ok:
                return
            fname = os.path.splitext(fname)[0]
            print( fname )
            g_orig = ROOT.gDirectory.FindObject( fname )




    # CANONIC ZOOM
    print(f"i... extracting /{g_orig.GetName()}/ of type /{g_orig.ClassName()}/")

    # -------------------------------   get Arrays -> import to numpy  .asarray
    if g_orig.ClassName()=="TGraph":
        x=np.asarray( g_orig.GetX() )
        y=np.asarray( g_orig.GetY() )
        dx = np.zeros_like(x)
        dy = np.zeros_like(y)+1
        print("!... UNIT ERROR SET ON Y-AXIS !!")

    if g_orig.ClassName()=="TGraphErrors":
        x=np.asarray( g_orig.GetX() )
        y=np.asarray( g_orig.GetY() )
        dx=np.asarray( g_orig.GetEX() )
        dy=np.asarray( g_orig.GetEY() )


    cala,calb=1,0
    if g_orig.ClassName()=="TH1D":
        #
        # i need to convert to np; be sure it is np.float64!
        # maybe - kill all zero points??? or set error 1??
        # ZOOM with GetFirst GetLast
        #
        #   x chan -0.5 to compensate midbin!
        #
        #  NASTY TRICK - x=x-zx1 -> and back...... I cannot converge at 7000chan
        #
        #
        zx1,zx2 = g_orig.GetXaxis().GetFirst(),g_orig.GetXaxis().GetLast()

        x  = np.asarray( np.arange( zx1,  zx2+1 ) ,  np.float64 )
        #
        # i have proble with large distances
        #
        #x  = np.asarray( np.arange( zx1-zx1,  zx2+1-zx1 ) ,  np.float64 )
        #x = x + 0.5 # bin center
        y  = np.zeros_like(x)
        dy = np.zeros_like(y)+1



        for i in range(zx1,zx2+1): # zx1,zx2+1 all range
            # i checked that I must -0.5 as bin[0] is underflow
            x[i-zx1] = float(x[i-zx1] - 0.5)
            y[i-zx1] = g_orig.GetBinContent( i)
            if y[i-zx1]>0:
                dy[i-zx1]=np.sqrt(y[i-zx1])
                #dy[i-zx1]=10

        dx = np.zeros_like(x)


        x = np.array(  x  ,  np.float64)
        y = np.array(  y  ,  np.float64)
        dx = np.array(  dx  ,  np.float64)
        dy = np.array(  dy  ,  np.float64)
        #dx=np.asarray( g_orig.GetEX() )
        #dy=np.asarray( g_orig.GetEY() )

        cala = (g_orig.GetXaxis().GetXmax() - g_orig.GetXaxis().GetXmin() )/( g_orig.GetNbinsX() )
        calb =  g_orig.GetXaxis().GetXmax() - cala*g_orig.GetNbinsX()
        # x = cala*x + calb



    # ///////////////////////////////////////////////////// plotting results

    #cmain = ROOT.gPad.GetCanvas()  # reset all canvas
    #cmain.Clear()
    #cmain = ROOT.gPad  # reset JUST THE PAD
    #cmain.Clear()
    #cmain.Divide(1,1) # div canvas
    #cmain.cd(1)

    ####g_xy = ROOT.TGraph( len(x) , x.flatten("C"), yf.flatten("C") )
    x12 = args[1].split(",")
    x12 = [ float(x) for x in x12 ]

    if x12[1]<x12[0]:
        dx = x12[1]
        x =  x12[0]
        x12[0] = x-dx
        x12[1] = x+dx

    #print(f"i... zooming to ")


    g_orig.GetXaxis().SetRangeUser( x12[0] , x12[1]  )
    # zoom works on energies!
    # g_orig.GetXaxis().SetRangeUser( (x12[0] - calb)/cala, (x12[1] - calb)/cala )

    if display:
        g_orig.SetMarkerStyle(7) # small circle , no lines...
        g_orig.Draw() # for histo NOT PAWL;  it works with NO PAWL TGraph too
        ROOT.gPad.Modified()
        ROOT.gPad.Update()



    #-------------------------- I NEED to REGISTER all to be able to display on gPad

#    prun.register(gf, "fit")




if __name__=="__main__":
    Fire(main)
    # update canvas
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    input('press ENTER to end...')
