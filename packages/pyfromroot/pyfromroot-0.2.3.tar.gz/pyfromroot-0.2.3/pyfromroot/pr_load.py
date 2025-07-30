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




def create_histo(df, hpos, cala, calb ):
    """
    TH1D * created
    """
    x = np.array(  df[ df.columns[hpos] ]  ,  np.float64)
    h = ROOT.TH1D( "h", "h", len(df), 0, len(df) )
    bn = 0
    for bc in x:
        bn+=1
        h.SetBinContent(  bn, bc )
    h.GetXaxis().SetLimits( calb, cala*len(df)+calb )
    return h








#---------------------------------------------
def main( *args , **kwargs):

    print(f"i... @pr_load MAIN: args={args}")
    if len(args)==0:
        print("X... no file given")
        return

    fname = args[0]
    if not os.path.exists( fname ):
        print(f"X... data file {fname} not found")
        return


    # - argument has a priority above LOAD_AS .......................
    xynames = None
    calibration = None # next part of argument
    if len(args)>1:
        print("d... argument for xy was sent...", args[1])
        # this must be the order:  xynames
        xynames = args[1]
        if type(xynames) is tuple: # in case of commandline operation
            #print("X... tuple")
            xynames = ",".join(xynames)
        xynames = xynames.split(",")
        print(f"i... order of columns is f{xynames}")

    else:
        print("D... ok, no argument that would take a priority")


    # - LOAD_AS x,y,dx,dy CODES for columns and COLNAMES inside the file ---
    #  and handle the priority of ARGS xydxdy ..............
    # names is nice columns names - xynames is x y dx dy
    names = []
    if xynames is None: xynames = []
    columns = 0


    # first try is searching for 10 lines and COLNAME: LOAD_AS
    #  1st line maybe #COLNAME without pragma?
    line1st = True
    line1stascolname = False
    line1stnames = [] # stays [] if False
    line1stheader = None # normally no header

    with open(fname) as f:
        #print("i... looking the file for COLNAMES: and LOAD_AS:")
        i = 0
        for com in f:
            com = com.strip()
            #print(com)
            i+=1
            if i>10: break
            com=com.strip()
            if com.find("#")<0:
                if line1st:
                    line1st = False
                    columns = com.split()
                    line1stnames = com.split()

                    # - at least twoONE values are float -> it is not a header
                    num_floats = 0
                    for i2 in columns:
                        if isfloat(i2):
                            num_floats+=1
                    if num_floats >= 1:
                        line1stascolname = False
                    else:
                        line1stascolname = True

                        # try:
                        #     float(i2) # if any of conversions is an error
                        # except:
                        #     line1stascolname = True

                columns = len(com.split())
            if com.find("#COLNAME:")==0:
                names2 = com.split(":")[1].strip().split(",")
                names = names2
                print("NAMES == {names}")

            if com.find("#LOAD_AS:")==0:
                # overrides?
                names2 = com.split(":")[1].strip().split(",")
                if (len(names2)>1)and( 'x' in names2)and('y' in names2): # x,y at least
                    if len(xynames)==0:
                        xynames = names2



    print("i... existing # of columns = ", columns)
    print("i... 1 COLNAME:",names)
    print("i... ... backup names = ", line1stnames)
    print("i... 1 LOAD_AS:" ,xynames)
    if line1stascolname:
        names = line1stnames
        line1stheader = 1
    #print(names,xynames)
    #--- here I must play with CALIB -------------------------------------
    cala = 1
    calb = 0
    for i in xynames:
        if i.find("cala=")==0: cala = float(i.split("=")[-1])
        if i.find("calb=")==0: calb = float(i.split("=")[-1])


    xynames = [x for x in xynames if x.find("cala=")!=0 and x.find("calb=")!=0]
    # DONE CALIB



    # ------ I may have names(column names) and xynames(the load order)

    # here I do the correct number of columns - BUTBUT later I do the same....
    while len(xynames)<columns:
        xynames.append(f"c_{len(xynames)}")

    for i in range(len(xynames)):
        if xynames[i]=="_":xynames[i]=f"col_{i}"
    for i in range(len(names)):
        if names[i]=="_":names[i]=f"col_{i}"


    if len(names)==0: names=xynames
    if len(names)!=len(xynames):
        print("!... redoing names",names)
        names=xynames



    #
    # HERE, all column names should be defined, if available
    # Order is defined by now
    #
    print("i... existing columns = ", columns)
    print("i... COLNAME:",names)
    print("i... LOAD_AS:" ,xynames)
    #print(names,xynames)


    # --- -if something is missing - quit
    histo = False
    if not( ('x' in xynames)and('y' in xynames) ):
        if not( ('h' in xynames) ):
            print("X... no <x> OR no <y> given; neither <h> for histogram" )
            print("X... try  x,y,dx,dy  or y,x ...." )
            return
        else:
            histo = True


    # count columns first to be sure it matches the names ;ADD fake colnames
    print("i... TRYING TO SUGGEST csv structure ............")
    #print(names)
    df = pd.read_csv(fname, delimiter="\s+", header=None, comment="#", nrows=2)
    i=1
    while len(names) <  df.shape[1]:
        names.append(f"col{i:d}")
        i+=1
    print("i... names==",names)

    if len(names)!=df.shape[1]:
        print(f"X... column problem: names={len(names)} i={i} dfcols={df.shape}" )

    # read all data now; column names are from COLNAMES or xynames(if not def)
    df = pd.read_csv(fname, delimiter="\s+", header=line1stheader, comment="#", names = names )
    print("---------------df---------------")
    print(df)

    #
    # HERE THE DF SHOULD BE PERFECTLY LOADED with colnames, defined x,y, maybe++
    #


    print("g... histo", histo )

    #------------------------------ HISTO OR GRAPH --------------
    if histo:
        hpos = xynames.index('h')
        print(f"i... h position {hpos}")
        print(f"i... hname= {names[hpos]} ")
        NAME1 = os.path.splitext(fname)[0]
    else:
        xpos = xynames.index('x')
        ypos = xynames.index('y')
        print(f"i... x position {xpos}  y position {ypos}")
        print(f"i... xname= {names[xpos]}  yname= {names[ypos]}")
        NAME1 = os.path.splitext(fname)[0]+f"_{names[xpos]}_{names[ypos]}"
    # ------ graph name in CLING - I enhance with variables - move after xpos
    #  I need to save 2 same graphs:
    #     - one without any _x_y to be accessible easily
    #     - one with _x_y that is specific and made accessible after more loads
    #


    NAMEO = os.path.splitext(fname)[0]
    print(f"D... graph name = {NAMEO}; for multiloads=>{NAME1} ")

    gontainer = None
    if histo:
        # it will be TH1D

        gontainer = create_histo(df, hpos, cala, calb)
        #gontainer.Draw()
        gontainer.SetTitle(f"{NAME1};channel;{names[hpos]}")
        #ROOT.gPad.SetLogy()
        gontainer.Print()


    else:
        # gontainer will be TGraphErrors
        print("g...  np array")
        x = np.array(  df[ df.columns[xpos] ]  ,  np.float64)
        y = np.array(  df[ df.columns[ypos] ]  ,  np.float64)

        #
        # check if dx and/or dy  given
        #

        if ('dx' in xynames)and('dy' in xynames):
            dxpos = xynames.index('dx')
            dypos = xynames.index('dy')
            dx = np.array(  df[ df.columns[dxpos] ]  ,  np.float64)
            dy = np.array(  df[ df.columns[dypos] ]  ,  np.float64)
            gontainer = ROOT.TGraphErrors( len(x) , x.flatten("C"), y.flatten("C"), dx.flatten("C"), dy.flatten("C") )
        elif ('dx' in xynames):
            dxpos = xynames.index('dx')
            dx = np.array(  df[ df.columns[dxpos] ]  ,  np.float64)
            dy = np.zeros_like(y)
            gontainer = ROOT.TGraphErrors( len(x) , x.flatten("C"), y.flatten("C"), dx.flatten("C"), dy.flatten("C") )
        elif ('dy' in xynames):
            dypos = xynames.index('dy')
            dy = np.array(  df[ df.columns[dypos] ]  ,  np.float64)
            dx = np.zeros_like(x)
            gontainer = ROOT.TGraphErrors( len(x) , x.flatten("C"), y.flatten("C"), dx.flatten("C"), dy.flatten("C") )
        else:
            print("g... gontainer TGraph")
            gontainer = ROOT.TGraph( len(x) , x.flatten("C"), y.flatten("C") )

        #
        # PLOT
        #  xpos and ypos are for axis labels
        #
        #g.Print()
        # plot nicely on (maybe new) TCanvas
        gontainer.SetMarkerStyle(7) # small circle , no lines...
        gontainer.SetMarkerStyle(1) # small circle , no lines...
        gontainer.SetMarkerStyle(22) # small...

        #g.SetName(f"{NAME1}") # done in prun register
        gontainer.SetTitle(f"{NAME1};{names[xpos]};{names[ypos]}")
        # AHAaaaa - I commented this out ....
        #gontainer.Draw("PAW") # no lines...

    # ------------------------------ END OF GRAPH / HISTO : common ----------
    #ROOT.gPad.SetGrid()
    prun.register(gontainer,NAME1) # register to SPecials with _x_y
    prun.register(gontainer,NAMEO) # register to SPecials sole simple
    #ROOT.gPad.Modified()
    #ROOT.gPad.Update()

    return





#############################################################################
if __name__=="__main__":
    Fire(main)
    print("H... close canvas to exit...")
    while ROOT.addressof(ROOT.gPad)!=0:
        time.sleep(0.2)
    #input('press ENTER to end...')
